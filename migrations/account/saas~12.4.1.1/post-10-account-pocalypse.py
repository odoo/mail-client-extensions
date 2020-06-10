# -*- coding: utf-8 -*-
from contextlib import contextmanager
import functools
import itertools
import logging
import operator
import os

from odoo.addons.base.maintenance.migrations import util
from odoo import fields


_logger = logging.getLogger("odoo.addons.base.maintenance.migrations.account.saas-12.4." + __name__)


def _convert_to_account_move_vals(inv_vals):
    """ Convert fetched account_invoice vals / account_voucher vals to account_move vals
    in order to create missing account_move for draft / cancelled invoices.
    This is needed to migrate old invoices to handle the account-pocalypse feature.

    :param inv_vals:    A python dict.
    :return:            A python dict to be passed to ['account.move'].create
    """
    return {
        # Mandatory fields.
        "type": inv_vals["type"],
        "date": inv_vals["date"] or fields.Date.today(),
        "state": inv_vals["state"],
        "partner_id": inv_vals["partner_id"],
        "journal_id": inv_vals["journal_id"],
        "currency_id": inv_vals["currency_id"],
        "invoice_date": inv_vals["invoice_date"],
        # Optional fields.
        "ref": inv_vals.get("ref"),
        "narration": inv_vals.get("narration"),
        "fiscal_position_id": inv_vals.get("fiscal_position_id"),
        "invoice_partner_bank_id": inv_vals.get("invoice_bank_partner_id"),
        "invoice_cash_rounding_id": inv_vals.get("invoice_cash_rounding_id"),
        "invoice_date_due": inv_vals.get("invoice_date_due"),
        "invoice_incoterm_id": inv_vals.get("invoice_incoterm_id"),
        "invoice_origin": inv_vals.get("invoice_origin"),
        "invoice_payment_ref": inv_vals.get("invoice_payment_ref"),
        "invoice_payment_term_id": inv_vals.get("invoice_payment_term_id"),
        "invoice_sent": inv_vals.get("invoice_sent"),
        "invoice_source_email": inv_vals.get("invoice_source_email"),
        "invoice_user_id": inv_vals.get("invoice_user_id"),
        "invoice_partner_display_name": inv_vals.get("invoice_partner_display_name"),
        # Lines.
        "invoice_line_ids": [
            (
                0,
                0,
                {
                    "name": inv_line_vals["name"],
                    "display_type": inv_line_vals.get("display_type"),
                    "sequence": inv_line_vals["sequence"],
                    "product_uom_id": inv_line_vals.get("product_uom_id"),
                    "product_id": inv_line_vals["product_id"],
                    "account_id": inv_line_vals["account_id"],
                    "price_unit": inv_line_vals["price_unit"],
                    "quantity": inv_line_vals["quantity"],
                    "discount": inv_line_vals.get("discount"),
                    "tax_ids": [(6, 0, [] if inv_line_vals.get("display_type") else inv_line_vals["tax_ids"])],
                    "analytic_account_id": inv_line_vals["analytic_account_id"],
                    "analytic_tag_ids": [(6, 0, inv_line_vals["analytic_tag_ids"])],
                },
            )
            for inv_line_vals in inv_vals.get("invoice_line_ids", [])
        ],
    }


def _explode_tax_groups(cr):
    _logger.info("Explode tax groups in child tax")
    cr.execute(
        """
        INSERT INTO account_invoice_line_tax (invoice_line_id, tax_id)
           SELECT ailt.invoice_line_id,child.child_tax
             FROM account_invoice_line_tax ailt
             JOIN account_tax t on ailt.tax_id=t.id
             JOIN account_tax_filiation_rel child on t.id=child.parent_tax
            WHERE t.amount_type='group'
       ON CONFLICT DO NOTHING
        """
    )
    cr.execute(
        """
        DELETE
          FROM account_invoice_line_tax ailt
         USING account_tax t, account_invoice_line l,account_invoice i
         WHERE t.amount_type='group'
           AND i.move_id IS NULL
           AND ailt.tax_id=t.id
           AND l.id=ailt.invoice_line_id
           AND i.id=l.invoice_id
    """
    )


def _get_conditions():
    # NOTE: as we ignore already matched lines, the conditions SHOULD be from more precise to less precise
    base_conditions = [
        {"same_name", "same_product", "exact_same_taxes"},
        {"same_name", "same_product", "same_taxes_from_company"},
        {"same_name", "same_product", "same_taxes_percentages"},
        {"same_not_null_product", "exact_same_taxes"},
        {"same_name", "exact_same_taxes"},
        # We now ignore the taxes if the invoice is paid and moved posted, trusting the accountant
        {"same_name", "same_product", "paid_invoice_posted_move"},
        {"same_not_null_product", "paid_invoice_posted_move"},
        {"same_name", "paid_invoice_posted_move"},
    ]

    def complete_conditions(*dimensions):
        def explode(iterables):
            return map(functools.partial(functools.reduce, operator.or_), itertools.product(*iterables))

        for xtr in explode(dimensions):
            for cond in base_conditions:
                yield cond | xtr
                if "same_name" in cond:
                    yield (cond - {"same_name"}) | {"same_trimmed_name"} | xtr
                    yield (cond - {"same_name"}) | {"same_chopped_name"} | xtr
                    yield (cond - {"same_name"}) | {"same_name_first_line"} | xtr
                    yield (cond - {"same_name"}) | {"substring_name"} | xtr

        yield {"same_amount", "only_one_line", "same_not_null_product"}
        for xtr in explode(dimensions):
            yield xtr | {"only_one_line"}

        for xtr in itertools.chain(*dimensions):
            yield xtr | {"only_one_line"}
        yield {"same_amount", "same_name", "same_not_null_product"}
        yield {"same_amount", "same_not_null_product"}

    # conditions = list(
    return iter(
        complete_conditions(
            [{"same_amount"}, {"nearly_same_amount"}],
            [
                {"same_analytic_account", "same_account"},
                {"same_account"},
                {"same_not_null_analytic_account"},
                {"only_one_line", "paid_invoice_posted_move"},
            ],
        )
    )


def _get_mapping_exceptions(name):
    return {int(a): int(b) for each in os.environ.get(name, "").split(",") for a, _, b in [each.partition(":")] if each}


def _compute_invoice_line_move_line_mapping(cr):
    """ Compute the mapping between account_invoice_line and its corresponding account_move_line.
    :param cr:      The database cursor.
    :return:        A map <invoice_line_id> -> <account_move_line_id>.
    """

    _logger.info("invoices: compute invoice line <-> move line mapping")

    # Create the reference table to log which condition creates the mapping.
    # This table is not dropped
    cr.execute(
        """
        CREATE TABLE _mig_134_invl_aml_cond_ref (
            cond_id INTEGER,
            cond_text VARCHAR
        )
        """
    )
    # We van start migration with an existing invl_aml_mapping, coming from a previous migration
    # To avoid computing something already computed many times
    if not util.table_exists(cr, "invl_aml_mapping"):
        # Create the mapping between account.invoice.line & account.move.line.
        cr.execute(
            """
            CREATE TABLE invl_aml_mapping (
                invl_id INTEGER NOT NULL,
                aml_id INTEGER NOT NULL,
                cond INTEGER
            )
            """
        )
        exc = _get_mapping_exceptions("MIG_S124_ACCOUNT_INVOICE_MAPPING")
        if exc:
            cr.executemany("INSERT INTO invl_aml_mapping(invl_id, aml_id) VALUES (%s, %s)", exc.items())
    else:
        cr.execute(
            "DELETE FROM invl_aml_mapping m WHERE NOT EXISTS (SELECT 1 FROM account_invoice_line l where l.id=m.invl_id)"
        )
        cr.execute(
            "DELETE FROM invl_aml_mapping m WHERE NOT EXISTS (SELECT 1 FROM account_move_line l where l.id=m.aml_id)"
        )

    remove_bad_matches_query = """
        WITH gb_ml AS (
            SELECT invl_id, array_agg(aml_id ORDER BY aml_id) as ml_ids
              FROM invl_aml_mapping
          GROUP BY invl_id
        ),
        gb_il AS (
            SELECT array_agg(invl_id) as il_ids, ml_ids
              FROM gb_ml
          GROUP BY ml_ids
        ),
        bad AS (
            -- get cartesian product of arrays
            -- see https://www.postgresql-archive.org/select-unnest-unnest-td6014421.html
            -- TODO: look at using LATERAL instead of a sub query
            SELECT unnest(il_ids) as il, ml
              FROM (
                SELECT il_ids, unnest(ml_ids) as ml
                  FROM gb_il
                 WHERE array_length(il_ids, 1) != array_length(ml_ids, 1)
              ) u
        )
        DELETE FROM invl_aml_mapping m
              USING bad
              WHERE m.invl_id = bad.il
                AND m.aml_id = bad.ml
          RETURNING m.invl_id, m.aml_id
    """

    filters = {
        "same_amount": """
            ROUND(il.price_subtotal - ml._mig_124_precomputed_amount,
                  curr.decimal_places) = 0.0
            """,
        # with a 0.01 tolerance
        "nearly_same_amount": """
            ABS(ROUND(il.price_subtotal - ml._mig_124_precomputed_amount,
                      curr.decimal_places)) <= curr.rounding
            """,
        "same_account": "il.account_id = ml.account_id",
        "same_name": "il.name = ml.name",
        # move line name used to be limited to 64 characters. See https://git.io/JeAmb
        "same_chopped_name": "substr(il.name, 0, 65) = ml.name",
        # ignoring trailing spaces
        "same_trimmed_name": r"regexp_replace(il.name, '\s*\Z', '') = regexp_replace(ml.name, '\s*\Z', '')",
        # invoice line name is a `fields.Text`, while move line name is a `fields.Char`.
        # Only match the first line
        "same_name_first_line": r"(regexp_match(il.name, '^(.*)$', 'n'))[1] = ml.name",
        # Sometimes, invoice line's name has been cut, move line's name must be used as prefix to match
        "substring_name": "strpos(ml.name, il.name) = 1",  # aka starts_with
        "same_product": "il.product_id IS NOT DISTINCT FROM ml.product_id",
        # When ignoring the name, the product should be not null
        "same_not_null_product": "il.product_id = ml.product_id",
        "same_analytic_account": """
             il.account_analytic_id IS NOT DISTINCT FROM ml.analytic_account_id
             AND
             ARRAY(SELECT r.account_analytic_tag_id
                     FROM account_analytic_tag_account_invoice_line_rel r
                    WHERE r.account_invoice_line_id = il.id
                 ORDER BY r.account_analytic_tag_id)
             =
             ARRAY(SELECT r.account_analytic_tag_id
                     FROM account_analytic_tag_account_move_line_rel r
                    WHERE r.account_move_line_id = ml.id
                 ORDER BY r.account_analytic_tag_id)
            """,
        "same_not_null_analytic_account": """
             il.account_analytic_id = ml.analytic_account_id
             AND
             ARRAY(SELECT r.account_analytic_tag_id
                     FROM account_analytic_tag_account_invoice_line_rel r
                    WHERE r.account_invoice_line_id = il.id
                 ORDER BY r.account_analytic_tag_id)
             =
             ARRAY(SELECT r.account_analytic_tag_id
                     FROM account_analytic_tag_account_move_line_rel r
                    WHERE r.account_move_line_id = ml.id
                 ORDER BY r.account_analytic_tag_id)
            """,
        "exact_same_taxes": """(
             ARRAY(SELECT r.tax_id
                     FROM account_invoice_line_tax r
                    WHERE r.invoice_line_id = il.id
                 ORDER BY r.tax_id)
             =
             ARRAY(SELECT r.account_tax_id
                     FROM account_move_line_account_tax_rel r
                    WHERE r.account_move_line_id = ml.id
                 ORDER BY r.account_tax_id)
            )""",
        "same_taxes_from_company": """(
             ARRAY(SELECT r.tax_id
                     FROM account_invoice_line_tax r
                     JOIN account_tax t ON t.id = r.tax_id
                    WHERE r.invoice_line_id = il.id
                      AND t.company_id = il.company_id
                 ORDER BY r.tax_id)
             =
             ARRAY(SELECT r.account_tax_id
                     FROM account_move_line_account_tax_rel r
                     JOIN account_tax t ON t.id = r.account_tax_id
                    WHERE r.account_move_line_id = ml.id
                      AND t.company_id = ml.company_id
                 ORDER BY r.account_tax_id)
           )""",
        "same_taxes_percentages": """(
             ARRAY(SELECT ROW(t.type_tax_use, t.amount, t.price_include)
                     FROM account_invoice_line_tax r
                     JOIN account_tax t ON t.id = r.tax_id
                    WHERE r.invoice_line_id = il.id
                      AND t.company_id = il.company_id
                      AND t.amount_type = 'percent'
                 ORDER BY t.type_tax_use, t.amount, t.price_include)
             =
             ARRAY(SELECT ROW(t.type_tax_use, t.amount, t.price_include)
                     FROM account_move_line_account_tax_rel r
                     JOIN account_tax t ON t.id = r.account_tax_id
                    WHERE r.account_move_line_id = ml.id
                      AND t.company_id = ml.company_id
                      AND t.amount_type = 'percent'
                 ORDER BY t.type_tax_use, t.amount, t.price_include)

             AND NOT EXISTS(
                   SELECT 1
                     FROM account_invoice_line_tax r
                     JOIN account_tax t ON t.id = r.tax_id
                    WHERE r.invoice_line_id = il.id
                      AND t.company_id = il.company_id
                      AND t.amount_type != 'percent'
                    UNION
                   SELECT 1
                     FROM account_move_line_account_tax_rel r
                     JOIN account_tax t ON t.id = r.account_tax_id
                    WHERE r.account_move_line_id = ml.id
                      AND t.company_id = ml.company_id
                      AND t.amount_type != 'percent'
             )
            )""",
        "paid_invoice_posted_move": "i.state IN ('open', 'paid') AND m.state = 'posted'",
        # only consider unmatched lines with the same amount
        "only_one_line": """
            NOT EXISTS(SELECT 1
                         FROM account_invoice_line ol
                        WHERE ol.display_type IS NULL
                          AND ol.invoice_id = il.invoice_id
                          AND ol.price_subtotal = il.price_subtotal
                          AND ol.id != il.id
                          AND NOT EXISTS(SELECT 1
                                           FROM invl_aml_mapping m
                                          WHERE m.invl_id = ol.id))""",
    }

    # precompute to speedup queries
    cr.execute("ALTER TABLE account_move_line ADD COLUMN _mig_124_precomputed_amount NUMERIC")
    cr.execute(
        """WITH computed AS
            (
            SELECT
                ml.id,
                (
                    CASE
                        WHEN i.currency_id = comp.currency_id
                        THEN ml.balance
                        ELSE ml.amount_currency
                    END
                    *
                    CASE i.type
                        WHEN 'out_invoice' THEN -1
                        WHEN 'in_invoice' THEN 1
                        WHEN 'out_refund' THEN 1
                        WHEN 'in_refund' THEN -1
                    END
                ) AS _mig_124_precomputed_amount
            FROM account_invoice i
            JOIN account_move m ON m.id = i.move_id
            JOIN account_move_line ml ON ml.move_id = m.id
            JOIN res_company comp ON comp.id = i.company_id
            JOIN res_currency curr ON curr.id = i.currency_id
        )
        UPDATE account_move_line l SET _mig_124_precomputed_amount = c._mig_124_precomputed_amount
          FROM computed c
         WHERE c.id = l.id"""
    )

    def generate_buckets():
        # Try to use different chunk sizes according to the number of invoice_line by invoice
        # To query takes a lot of time when there are invoices with many invoice lines
        # For single invoice line process by chunk of 500, for medium size invoices(between 10 or 20 invoice lines process by 25)

        cr.execute(
            """
            WITH invoices0 AS (
                SELECT il.invoice_id as id,
                    CASE
                    WHEN count(*)<=2 THEN 500
                    WHEN count(*)<=5 THEN 100
                    WHEN count(*)<=10 THEN 50
                    WHEN count(*)<=20 THEN 25
                    ELSE 2
                    END as inv_group
                        FROM account_invoice_line il
                LEFT JOIN invl_aml_mapping mp ON il.id = mp.invl_id
                GROUP BY il.invoice_id
                HAVING count(*) <> count(mp.invl_id)
                ),
                buckets_per_group AS (
                    SELECT inv_group, (count(*) / inv_group)::integer + 1 as buckets
                    FROM invoices0
                    GROUP BY inv_group
                ),
                invoices as (
                    SELECT i.*,
                        NTILE(buckets) OVER(PARTITION BY i.inv_group) as chunk
                    FROM invoices0 i
                    JOIN buckets_per_group b ON i.inv_group = b.inv_group
                )
                SELECT (array_agg(id))ids
                  FROM invoices
              GROUP BY inv_group,
                       chunk
        """
        )
        return [r[0] for r in cr.fetchall()]

    with util.temp_index(cr, "invl_aml_mapping", "invl_id"), util.temp_index(cr, "invl_aml_mapping", "aml_id"):
        chunks = generate_buckets()
        # use a temporary table to makes parallel inserts
        # Allow to better parallelize with conditions NOT EXISTS(...in invl_aml_mapping)
        cr.execute(
            """
                CREATE TABLE invl_aml_mapping_temp (
                    invl_id INTEGER NOT NULL,
                    aml_id INTEGER NOT NULL,
                    cond INTEGER
                )
                """
        )

        # execute the query in mutli-passes (leeloo?)
        for i, cond in enumerate(_get_conditions(), start=1):
            _logger.info("insert query %s: cond:%s", i, cond)
            cr.execute("TRUNCATE TABLE invl_aml_mapping_temp")
            query = """
                INSERT INTO invl_aml_mapping_temp(invl_id, aml_id, cond)
                SELECT il.id, ml.id, %s
                    FROM account_invoice_line il
                    JOIN account_invoice i ON i.id = il.invoice_id
                    JOIN account_move m ON m.id = i.move_id
                    JOIN account_move_line ml ON ml.move_id = m.id
                    JOIN res_company comp ON comp.id = i.company_id
                    JOIN res_currency curr ON curr.id = i.currency_id
                WHERE il.display_type IS NULL
                  AND NOT EXISTS (SELECT invl_id FROM invl_aml_mapping WHERE invl_id=il.id)
                  AND NOT EXISTS (SELECT aml_id FROM invl_aml_mapping WHERE aml_id=ml.id)
                  AND i.id = ANY(%s)
                  AND {}
            """.format(
                " AND ".join(filters[c] for c in cond)
            )
            queries = []
            for chunk in chunks:
                queries.append(cr.mogrify(query, (i, chunk)))
            util.parallel_execute(cr, queries)
            cr.execute(
                """
            INSERT INTO _mig_134_invl_aml_cond_ref (cond_id,cond_text)
            VALUES(%s, %s)""",
                (i, ", ".join(cond)),
            )
            cr.execute(
                """INSERT INTO invl_aml_mapping(invl_id, aml_id, cond)
            SELECT invl_id, aml_id, cond FROM invl_aml_mapping_temp
            """
            )
            added = cr.rowcount
            if added:
                # reevaluate the chunks, don't loop to invoices having already all the lines mapped
                chunks = generate_buckets()
                cr.execute(remove_bad_matches_query)
                removed = cr.rowcount
            else:
                removed = 0

            _logger.info("invoices: fill line mapping with +%d/-%d entries using conditions %r", added, removed, cond)

            cr.execute(
                """
                SELECT count(l.id)
                  FROM account_invoice_line l
             LEFT JOIN invl_aml_mapping m ON l.id=m.invl_id
                 WHERE l.display_type IS NULL
                   AND l.price_subtotal != 0
                   AND m.invl_id IS NULL
            """
            )
            rem = cr.fetchone()[0]
            if rem == 0:
                break
            _logger.info("invoices: still %d to match", rem)

    # clean optimizations
    cr.execute("ALTER TABLE account_move_line DROP COLUMN _mig_124_precomputed_amount")
    cr.execute("DROP TABLE invl_aml_mapping_temp")

    # create move line for non matching invoice lines with subtotal zero
    env = util.env(cr)
    MoveLine = env["account.move.line"]

    cr.execute(
        """
        SELECT l.id, i.move_id, l.name, l.product_id, l.account_id, l.uom_id,
               l.price_unit, l.discount, l.sequence,
               l.account_analytic_id,
               array_remove(array_agg(x.tax_id), NULL) as taxes,
               array_remove(array_agg(g.account_analytic_tag_id), NULL) as tags

          FROM account_invoice_line l
          JOIN account_invoice i ON i.id = l.invoice_id
     LEFT JOIN account_invoice_line_tax x ON x.invoice_line_id = l.id
     LEFT JOIN account_analytic_tag_account_invoice_line_rel g ON g.account_invoice_line_id = l.id
     LEFT JOIN invl_aml_mapping m ON l.id=m.invl_id
         WHERE l.display_type IS NULL
           AND m.invl_id IS NULL
           AND l.price_subtotal = 0
      GROUP BY l.id, i.move_id, l.name, l.product_id, l.account_id, l.uom_id,
               l.price_unit, l.discount, l.sequence,
               l.account_analytic_id
    """
    )
    mls = []
    line_ids = []
    for line in util.log_progress(cr.dictfetchall(), qualifier="zero-line", logger=_logger):
        line_ids.append(line["id"])
        mls.append(
            {
                "move_id": line["move_id"],
                "name": line["name"],
                "sequence": line["sequence"],
                "product_uom_id": line["uom_id"],
                "product_id": line["product_id"],
                "account_id": line["account_id"],
                "price_unit": line["price_unit"],
                # Force quantity to 0 to force the subtotal to be computed to 0
                # In some cases, the subtotal on the invoice line is 0, but price unit * quantity * discount is not,
                # and the override of the move line `create` will recompute the subtotal according to these.
                # https://github.com/odoo/odoo/blob/c5cd7329529cfa27d1f65217bd54042642711048/addons/account/models/account_move.py#L3307
                # It doesn't matter setting the quantity to 0 here, because it's reset with the correct quantity at the end of this method
                # with a raw `UPDATE` sql on `account_move_line`, updating the quantity according to the invoice line.
                "quantity": 0,
                "discount": line["discount"],
                "credit": 0,
                "debit": 0,
                "tax_ids": [(6, 0, line["taxes"])],
                "analytic_account_id": line["account_analytic_id"],
                "analytic_tag_ids": [(6, 0, line["tags"])],
            }
        )
    _logger.info("invoices: creating zero-line move.line")
    ml_ids = MoveLine.create(mls).ids
    _logger.info("invoices: creating zero-line mapping")
    cr.executemany("INSERT INTO invl_aml_mapping(invl_id, aml_id,cond) VALUES (%s, %s, 0)", zip(line_ids, ml_ids))

    # constistancy check
    _logger.info("invoices: ensuring consistant mapping")
    cr.execute(remove_bad_matches_query)
    cr.execute(
        """
        WITH gb_ml AS (
            SELECT invl_id, array_agg(aml_id ORDER BY aml_id) as ml_ids
              FROM invl_aml_mapping
          GROUP BY invl_id
        )
        SELECT array_agg(invl_id) as invls, ml_ids as amls
       -- INTO TEMPORARY TABLE saas124_acc_mig_bad_mappings
          INTO TABLE saas124_acc_mig_bad_mappings
          FROM gb_ml
      GROUP BY ml_ids
    HAVING NOT (count(invl_id) = 1 and array_length(ml_ids,1)=1)
    """
    )
    # use unnest,unnest as `zip` (works in any pg version because both arrays have the same length)
    # See https://www.postgresql-archive.org/select-unnest-unnest-td6014421.html
    cr.execute(
        """
        WITH same_length AS (
            DELETE FROM saas124_acc_mig_bad_mappings
             WHERE array_length(invls, 1) = array_length(amls, 1)
         RETURNING invls, amls
        ),
        todel AS (
            SELECT unnest(invls) as il, unnest(amls) as ml
              FROM same_length
        )
        DELETE FROM invl_aml_mapping m
              USING todel t
              WHERE m.invl_id = t.il
                AND m.aml_id != t.ml
    """
    )

    cr.execute("SELECT invls, amls FROM saas124_acc_mig_bad_mappings")
    for i, a in cr.fetchall():
        _logger.error("Invalid invoice line <-> move line mapping: %r <-> %r", i, a)

    cr.commit()

    # if cr.rowcount:
    #     raise util.MigrationError("bad invoice mapping found")

    search_missing_mapping = """
        SELECT count(l.id), string_agg(l.id::text, ',' ORDER BY l.id)
          FROM account_invoice_line l
     LEFT JOIN invl_aml_mapping m ON l.id=m.invl_id
         WHERE l.display_type IS NULL
           AND m.invl_id IS NULL
    """
    cr.execute(search_missing_mapping)
    cnt, ids = cr.fetchone()
    if cnt:
        _compute_invoice_line_grouped_in_move_line(cr)

    cr.execute(search_missing_mapping)
    cnt, ids = cr.fetchone()
    if cnt:
        _logger.error("Missing move line for %s invoice lines: %s", cnt, ids)
        raise util.MigrationError("Some account.invoice.line have no account.move.line")

    _logger.info("invoices: indexing move lines mapping")
    cr.execute("create UNIQUE index on invl_aml_mapping(invl_id)")
    cr.execute("create index on invl_aml_mapping(aml_id)")

    _logger.info("invoices: copy business fields from voucher lines to move lines")
    with util.disable_triggers(cr, "account_move_line"):
        cr.execute(
            """
            UPDATE account_move_line aml
               SET quantity = invl.quantity,
                   price_unit = invl.price_unit,
                   discount = invl.discount,
                   price_subtotal = invl.price_subtotal,
                   price_total = invl.price_total
              FROM invl_aml_mapping mapping
        INNER JOIN account_invoice_line invl ON invl.id = mapping.invl_id
             WHERE mapping.aml_id = aml.id
            """
        )


@contextmanager
def no_fiscal_lock(cr):
    cr.execute(
        """
        UPDATE res_company c
           SET tax_lock_date = NULL,
               period_lock_date = NULL,
               fiscalyear_lock_date = NULL
          FROM res_company old
         WHERE old.id = c.id
     RETURNING old.tax_lock_date, old.period_lock_date, old.fiscalyear_lock_date, old.id
    """
    )
    data = cr.fetchall()
    yield
    cr.executemany(
        """
        UPDATE res_company
           SET tax_lock_date = %s,
               period_lock_date = %s,
               fiscalyear_lock_date = %s
         WHERE id = %s

    """,
        data,
    )


def migrate_voucher_lines(cr):
    def _get_voucher_conditions():
        yield from _get_conditions()
        yield {"same_name", "same_not_null_analytic_account", "only_one_line"}

    env = util.env(cr)
    # cleanup
    cr.execute("DELETE FROM account_voucher_line WHERE voucher_id IS NULL")

    # explode taxes
    _logger.info("vouchers: explode tax groups in child tax")
    cr.execute(
        """
        INSERT INTO account_tax_account_voucher_line_rel(account_voucher_line_id, account_tax_id)
             SELECT r.account_voucher_line_id, child.child_tax
               FROM account_tax_account_voucher_line_rel r
               JOIN account_tax t ON r.account_tax_id = t.id
               JOIN account_tax_filiation_rel child ON t.id = child.parent_tax
              WHERE t.amount_type = 'group'
        """
    )
    cr.execute(
        """
        DELETE FROM account_tax_account_voucher_line_rel r
              USING account_tax t, account_voucher_line l, account_voucher v
       WHERE t.amount_type = 'group'
         AND v.move_id IS NULL
         AND r.account_tax_id=t.id
         AND l.id = r.account_voucher_line_id
         AND v.id = l.voucher_id
        """
    )

    # In case a draft of cancelled voucher has a different company than its journal (incorrect, but can happen),
    # we change its journal to assign it to the first one of the right type available for this company
    _logger.info("vouchers: fixing journal issues")
    # TODO : Revamp in SQL
    for company in env["res.company"].search([]):
        cr.execute(
            """
            SELECT journal.type as journal_type, array_agg(inv.id) as ids
              FROM account_voucher inv
              JOIN account_journal journal ON journal.id = inv.journal_id
             WHERE inv.company_id != journal.company_id
               AND inv.state IN ('draft', 'cancel')
               AND inv.company_id = %(company)s
          GROUP BY journal.type
        """,
            {"company": company.id},
        )

        to_fix = cr.dictfetchall()
        for data_dict in to_fix:
            journal = env["account.journal"].search(
                [("type", "=", data_dict["journal_type"]), ("company_id", "=", company.id)], limit=1
            )
            if not journal:
                raise util.MigrationError(
                    f"Company {company.id} has `draft` or `canceled` vouchers on journals belonging to a different company, "
                    "but does not have any equivalent journal allowing to fix that. Manual intervention is required."
                )

            cr.execute(
                """
                UPDATE account_voucher
                   SET journal_id = %(journal)s
                 WHERE id IN %(ids)s
            """,
                {"journal": journal.id, "ids": tuple(data_dict["ids"])},
            )

    # create moves for draft/cancel vouchers
    _logger.info("vouchers: create missing account moves")
    vouchers = {}
    cr.execute(
        """
        SELECT inv.id,
               CASE WHEN inv.voucher_type = 'sale' THEN 'out_receipt' ELSE 'in_receipt' END
                                                   AS type,
               inv.name                            AS ref,
               inv.date                            AS invoice_date,
               inv.date_due                        AS invoice_due_date,
               inv.account_date                    AS date,
               inv.journal_id,
               inv.narration,
               inv.currency_id,
               inv.state,
               inv.reference,
               inv.partner_id
          FROM account_voucher inv
         WHERE inv.state IN ('draft', 'cancel')
    """
    )
    for vals in cr.dictfetchall():
        vouchers[vals["id"]] = vals
    if vouchers:
        cr.execute(
            """
            SELECT
                inv_line.name,
                inv_line.sequence,
                inv_line.voucher_id,
                inv_line.product_id,
                inv_line.account_id,
                inv_line.price_unit,
                inv_line.quantity,
                array_remove(ARRAY_AGG(inv_line_tax.account_tax_id), NULL) AS tax_ids,
                inv_line.account_analytic_id AS analytic_account_id,
                array_remove(ARRAY_AGG(tags.account_analytic_tag_id), NULL) AS analytic_tag_ids
            FROM account_voucher_line inv_line
            LEFT JOIN account_tax_account_voucher_line_rel inv_line_tax ON inv_line_tax.account_voucher_line_id = inv_line.id
            LEFT JOIN account_analytic_tag_account_invoice_line_rel tags ON tags.account_invoice_line_id = inv_line.id
            WHERE inv_line.voucher_id IN %s
            GROUP BY
                inv_line.id,
                inv_line.name,
                inv_line.sequence,
                inv_line.voucher_id,
                inv_line.product_id,
                inv_line.account_id,
                inv_line.price_unit,
                inv_line.quantity,
                inv_line.account_analytic_id
            ORDER BY inv_line.sequence, inv_line.id
        """,
            [tuple(vouchers)],
        )
        for line_vals in cr.dictfetchall():
            vouchers[line_vals["voucher_id"]].setdefault("invoice_line_ids", []).append(line_vals)

    Move = env["account.move"].with_context(check_move_validity=False)
    created_moves = Move.browse()
    for record_id, vals in util.log_progress(vouchers.items(), qualifier="vouchers", logger=_logger):
        try:
            with util.savepoint(cr):
                created_move = Move.create(_convert_to_account_move_vals(vals))
                created_moves |= created_move
                # Store link to newly created account_moves.
                cr.execute("UPDATE account_voucher SET move_id=%s WHERE id=%s", [created_move.id, record_id])
        except Exception:
            _logger.exception("Cannot create move from draft/cancel voucher")

    _logger.info("vouchers: compute voucher line -> move line mapping")
    cr.execute(
        """
        CREATE TABLE vl_ml_mapping (
            vl_id INTEGER NOT NULL,
            ml_id INTEGER NOT NULL
        )
        """
    )
    exc = _get_mapping_exceptions("MIG_S124_ACCOUNT_VOUCHER_MAPPING")
    if exc:
        cr.executemany("INSERT INTO vl_ml_mapping(vl_id, ml_id) VALUES (%s, %s)", exc.items())

    remove_bad_matches_query = """
        WITH gb_ml AS (
            SELECT vl_id, array_agg(ml_id ORDER BY ml_id) as ml_ids
              FROM vl_ml_mapping
          GROUP BY vl_id
        ),
        gb_vl AS (
            SELECT array_agg(vl_id ORDER BY vl_id) as vl_ids, ml_ids
              FROM gb_ml
          GROUP BY ml_ids
        ),
        bad AS (
            -- get cartesian product of arrays
            -- see https://www.postgresql-archive.org/select-unnest-unnest-td6014421.html
            -- TODO: look at using LATERAL instead of a sub query
            SELECT unnest(vl_ids) as vl, ml
              FROM (
                SELECT vl_ids, unnest(ml_ids) as ml
                  FROM gb_vl
                 WHERE array_length(vl_ids, 1) != array_length(ml_ids, 1)
              ) u
        )
        DELETE FROM vl_ml_mapping m
              USING bad
              WHERE m.vl_id = bad.vl
                AND m.ml_id = bad.ml
            RETURNING m.vl_id,m.ml_id
    """

    filters = {
        "same_amount": """
            ROUND(il.price_subtotal - (CASE WHEN i.currency_id = comp.currency_id
                                            THEN ml.balance
                                            ELSE ml.amount_currency
                                       END * CASE i.voucher_type
                                                WHEN 'purchase' THEN 1
                                                WHEN 'sale' THEN -1
                                             END),
                  curr.decimal_places) = 0.0
            """,
        # with a 0.01 tolerance
        "nearly_same_amount": """
            ABS(ROUND(il.price_subtotal - (CASE WHEN i.currency_id = comp.currency_id
                                                THEN ml.balance
                                                ELSE ml.amount_currency
                                           END * CASE i.voucher_type
                                                    WHEN 'purchase' THEN 1
                                                    WHEN 'sale' THEN -1
                                                 END),
                      curr.decimal_places)) <= curr.rounding
            """,
        "same_account": "il.account_id = ml.account_id",
        "same_name": "il.name = ml.name",
        # move line name used to be limited to 64 characters. See https://git.io/JeAmb
        "same_chopped_name": "substr(il.name, 0, 65) = ml.name",
        # ignoring trailing spaces
        "same_trimmed_name": r"regexp_replace(il.name, '\s*\Z', '') = regexp_replace(ml.name, '\s*\Z', '')",
        # invoice line name is a `fields.Text`, while move line name is a `fields.Char`.
        # Only match the first line
        "same_name_first_line": r"(regexp_match(il.name, '^(.*)$', 'n'))[1] = ml.name",
        # Sometimes, invoice line's name has been cut, move line's name must be used as prefix to match
        "substring_name": "strpos(ml.name, il.name) = 1",  # aka starts_with
        "same_product": "il.product_id IS NOT DISTINCT FROM ml.product_id",
        # When ignoring the name, the product should be not null
        "same_not_null_product": "il.product_id = ml.product_id",
        "same_analytic_account": """
             il.account_analytic_id IS NOT DISTINCT FROM ml.analytic_account_id
             AND
             ARRAY(SELECT r.account_analytic_tag_id
                     FROM account_analytic_tag_account_voucher_line_rel r
                    WHERE r.account_voucher_line_id = il.id
                 ORDER BY r.account_analytic_tag_id)
             =
             ARRAY(SELECT r.account_analytic_tag_id
                     FROM account_analytic_tag_account_move_line_rel r
                    WHERE r.account_move_line_id = ml.id
                 ORDER BY r.account_analytic_tag_id)
            """,
        "same_not_null_analytic_account": """
             il.account_analytic_id = ml.analytic_account_id
             AND
             ARRAY(SELECT r.account_analytic_tag_id
                     FROM account_analytic_tag_account_voucher_line_rel r
                    WHERE r.account_voucher_line_id = il.id
                 ORDER BY r.account_analytic_tag_id)
             =
             ARRAY(SELECT r.account_analytic_tag_id
                     FROM account_analytic_tag_account_move_line_rel r
                    WHERE r.account_move_line_id = ml.id
                 ORDER BY r.account_analytic_tag_id)
            """,
        "exact_same_taxes": """(
             ARRAY(SELECT r.account_tax_id
                     FROM account_tax_account_voucher_line_rel r
                    WHERE r.account_voucher_line_id = il.id
                 ORDER BY r.account_tax_id)
             =
             ARRAY(SELECT r.account_tax_id
                     FROM account_move_line_account_tax_rel r
                    WHERE r.account_move_line_id = ml.id
                 ORDER BY r.account_tax_id)
            )""",
        "same_taxes_from_company": """(
             ARRAY(SELECT r.account_tax_id
                     FROM account_tax_account_voucher_line_rel r
                     JOIN account_tax t ON t.id = r.account_tax_id
                    WHERE r.account_voucher_line_id = il.id
                      AND t.company_id = il.company_id
                 ORDER BY r.account_tax_id)
             =
             ARRAY(SELECT r.account_tax_id
                     FROM account_move_line_account_tax_rel r
                     JOIN account_tax t ON t.id = r.account_tax_id
                    WHERE r.account_move_line_id = ml.id
                      AND t.company_id = ml.company_id
                 ORDER BY r.account_tax_id)
           )""",
        "same_taxes_percentages": """(
             ARRAY(SELECT ROW(t.type_tax_use, t.amount, t.price_include)
                     FROM account_tax_account_voucher_line_rel r
                     JOIN account_tax t ON t.id = r.account_tax_id
                    WHERE r.account_voucher_line_id = il.id
                      AND t.company_id = il.company_id
                      AND t.amount_type = 'percent'
                 ORDER BY t.type_tax_use, t.amount, t.price_include)
             =
             ARRAY(SELECT ROW(t.type_tax_use, t.amount, t.price_include)
                     FROM account_move_line_account_tax_rel r
                     JOIN account_tax t ON t.id = r.account_tax_id
                    WHERE r.account_move_line_id = ml.id
                      AND t.company_id = ml.company_id
                      AND t.amount_type = 'percent'
                 ORDER BY t.type_tax_use, t.amount, t.price_include)

             AND NOT EXISTS(
                   SELECT 1
                     FROM account_tax_account_voucher_line_rel r
                     JOIN account_tax t ON t.id = r.account_tax_id
                    WHERE r.account_voucher_line_id = il.id
                      AND t.company_id = il.company_id
                      AND t.amount_type != 'percent'
                    UNION
                   SELECT 1
                     FROM account_move_line_account_tax_rel r
                     JOIN account_tax t ON t.id = r.account_tax_id
                    WHERE r.account_move_line_id = ml.id
                      AND t.company_id = ml.company_id
                      AND t.amount_type != 'percent'
             )
            )""",
        "paid_invoice_posted_move": "i.state = 'posted' AND m.state = 'posted'",
        # only consider unmatched lines with the same amount
        "only_one_line": """
            NOT EXISTS(SELECT 1
                         FROM account_voucher_line ol
                        WHERE ol.voucher_id = il.voucher_id
                          AND ol.price_subtotal = il.price_subtotal
                          AND ol.id != il.id
                          AND NOT EXISTS(SELECT 1
                                           FROM vl_ml_mapping m
                                          WHERE m.vl_id = ol.id))""",
    }

    for cond in _get_voucher_conditions():
        cr.execute(
            """
            INSERT INTO vl_ml_mapping(vl_id, ml_id)
            SELECT il.id, ml.id
              FROM account_voucher_line il
              JOIN account_voucher i ON i.id = il.voucher_id
              JOIN account_move m ON m.id = i.move_id
              JOIN account_move_line ml ON ml.move_id = m.id
              JOIN res_company comp ON comp.id = i.company_id
              JOIN res_currency curr ON curr.id = i.currency_id

             WHERE il.price_subtotal != 0
               AND il.id NOT IN (SELECT vl_id FROM vl_ml_mapping)
               AND ml.id NOT IN (SELECT ml_id FROM vl_ml_mapping)

               AND {}
        """.format(
                " AND ".join(filters[c] for c in cond)
            )
        )
        added = cr.rowcount

        if added:
            cr.execute(remove_bad_matches_query)
            removed = cr.rowcount
        else:
            removed = 0

        _logger.info("vouchers: fill line mapping with +%d/-%d entries using conditions %r", added, removed, cond)

        cr.execute(
            """
            SELECT count(l.id)
              FROM account_voucher_line l
              JOIN account_voucher v ON v.id = l.voucher_id
         LEFT JOIN vl_ml_mapping m ON l.id = m.vl_id
             WHERE m.vl_id IS NULL
               AND l.price_subtotal != 0
               AND v.move_id IS NOT NULL
        """
        )
        rem = cr.fetchone()[0]
        if rem == 0:
            break
        _logger.info("vouchers: still %d to match", rem)

    _logger.info("vouchers: ensuring consistant mapping")
    cr.execute(remove_bad_matches_query)
    cr.execute(
        """
        WITH gb_ml AS (
            SELECT vl_id, array_agg(ml_id ORDER BY ml_id) as ml_ids
              FROM vl_ml_mapping
          GROUP BY vl_id
        )
        SELECT array_agg(vl_id ORDER BY vl_id) as vls, ml_ids as mls
       -- INTO TEMPORARY TABLE saas124_acc_mig_bad_voucher_mapping
          INTO TABLE saas124_acc_mig_bad_voucher_mapping
          FROM gb_ml
      GROUP BY ml_ids
    HAVING NOT (count(vl_id) = 1 and array_length(ml_ids,1)=1)
    """
    )
    # use unnest,unnest as `zip` (works in any pg version because both arrays have the same length)
    # See https://www.postgresql-archive.org/select-unnest-unnest-td6014421.html
    cr.execute(
        """
        WITH same_length AS (
            DELETE FROM saas124_acc_mig_bad_voucher_mapping
             WHERE array_length(vls, 1) = array_length(mls, 1)
         RETURNING vls, mls
        ),
        todel AS (
            SELECT unnest(vls) as vl, unnest(mls) as ml
              FROM same_length
        )
        DELETE FROM vl_ml_mapping m
              USING todel t
              WHERE m.vl_id = t.vl
                AND m.ml_id != t.ml
    """
    )

    cr.execute("SELECT vls, mls FROM saas124_acc_mig_bad_voucher_mapping")
    for v, m in cr.fetchall():
        _logger.error("vouchers: invalid line mapping: %r <-> %r", v, m)

    _logger.info("vouchers: check for missing line mapping")  # ignoring line with amount = 0
    cr.execute(
        """
        SELECT count(l.id), string_agg(l.id::text, ',' ORDER BY l.id)
          FROM account_voucher_line l
          JOIN account_voucher v ON v.id = l.voucher_id
     LEFT JOIN vl_ml_mapping m ON l.id = m.vl_id
         WHERE m.vl_id IS NULL
           AND l.price_subtotal != 0
           AND v.move_id IS NOT NULL
    """
    )
    cnt, ids = cr.fetchone()
    if cnt:
        _logger.error("vouchers: missing move line for %s voucher lines: %s", cnt, ids)
        raise util.MigrationError("Some account.voucher.line have no account.move.line")

    _logger.info("vouchers: copy business fields from voucher lines to move lines")
    cr.execute(
        """
        UPDATE account_move_line m
        SET quantity = v.quantity,
            price_unit = v.price_unit,
            price_subtotal = v.price_subtotal,
            exclude_from_invoice_tab = FALSE
        FROM vl_ml_mapping g
        JOIN account_voucher_line v ON v.id = g.vl_id
        WHERE g.ml_id = m.id
        """
    )

    # cr.execute("CREATE UNIQUE INDEX ON vl_ml_mapping(vl_id)")
    # cr.execute("CREATE INDEX ON vl_ml_mapping(ml_id)")


def _compute_invoice_line_grouped_in_move_line(cr):
    # "tax_ids": [(6, 0, [] if inv_line_vals.get("display_type") else inv_line_vals["tax_ids"])],
    # "analytic_tag_ids": [(6, 0, inv_line_vals["analytic_tag_ids"])],
    cr.execute("ALTER TABLE account_move_line ADD COLUMN _mig124_invl_id int4")
    cr.execute(
        """
        INSERT INTO account_move_line (
            move_id, move_name, date, ref, parent_state, journal_id, company_id, company_currency_id,
            account_id,account_internal_type,account_root_id,sequence,name,quantity,price_unit,discount,
            display_type,is_rounding_line,exclude_from_invoice_tab,analytic_account_id,
            debit,credit,balance,amount_currency,price_subtotal,price_total,reconciled,blocked,
            currency_id,partner_id,product_uom_id,product_id,_mig124_invl_id
        )
        SELECT m.id,
               m.name,
               m.date,
               m.ref,
               m.state,
               m.journal_id,
               m.company_id,
               c.currency_id,
               NULL, -- l.account_id,
               aat.type,
               a.root_id,
               l.sequence,
               l.name,
               l.quantity,
               l.price_unit,
               l.discount,
               'line_note',
               FALSE,
               FALSE,
               l.account_analytic_id,
               0,
               0,
               0,
               0,
               0,
               0,
               TRUE,
               FALSE,
               NULL, -- l.currency_id,
               l.partner_id,
               l.uom_id,
               l.product_id,
               l.id
          FROM account_invoice_line l
          JOIN account_invoice i ON l.invoice_id=i.id
          JOIN account_move m ON m.id=i.move_id
     LEFT JOIN res_company c ON m.company_id=c.id
     LEFT JOIN account_account a ON l.account_id=a.id
     LEFT JOIN account_account_type aat ON aat.id=a.user_type_id

         WHERE l.id NOT IN (SELECT invl_id FROM invl_aml_mapping)
    """
    )
    cr.execute(
        """
        INSERT INTO invl_aml_mapping (invl_id,aml_id,cond)
        SELECT _mig124_invl_id,id,9999 FROM account_move_line WHERE _mig124_invl_id IS NOT NULL
    """
    )
    cr.execute("ALTER TABLE account_move_line DROP COLUMN _mig124_invl_id")


def migrate_invoice_lines(cr):
    env = util.env(cr)
    invoices = {}

    # =======================================================================================
    # Migrate account_invoice to account_move
    # =======================================================================================
    cr.execute("DELETE FROM account_invoice_line WHERE invoice_id IS NULL")
    _explode_tax_groups(cr)

    # In case a draft of cancelled invoice has a different company than its journal (incorrect, but can happen),
    # we change its journal to assign it to the first one of the right type available for this company
    _logger.info("invoices: fixing journal issues")
    for company in env["res.company"].search([]):
        cr.execute(
            """
            SELECT journal.type as journal_type, array_agg(inv.id) as ids
              FROM account_invoice inv
              JOIN account_journal journal ON journal.id = inv.journal_id
             WHERE inv.company_id != journal.company_id
               AND inv.state IN ('draft', 'cancel')
               AND inv.company_id = %(company)s
          GROUP BY journal.type
        """,
            {"company": company.id},
        )

        for journal_type, ids in cr.fetchall():

            journal = env["account.journal"].search(
                [("type", "=", journal_type), ("company_id", "=", company.id)], limit=1
            )
            if not journal:
                raise util.MigrationError(
                    "Company {company.id} has `draft` or `canceled` vouchers on journals belonging to a different company, "
                    "but does not have any equivalent journal allowing to fix that. Manual intervention is required."
                )

            cr.execute(
                """
                UPDATE account_invoice
                   SET journal_id = %(journal)s
                 WHERE id IN %(ids)s
            """,
                {"journal": journal.id, "ids": tuple(ids)},
            )

    # Create account_move for draft account_invoice.
    no_create_state = (
        "in_payment",
        "open",
        "paid",
    )
    if os.getenv("MIG_CREATE_MISSING_MOVES"):
        # if env var is set, allow to create draft dor open and paid invoices
        no_create_state = ("in_payment",)
    cr.execute(
        """
        SELECT
            inv.id,
            inv.currency_id,
            inv.date,
            inv.fiscal_position_id,
            inv.cash_rounding_id                    AS invoice_cash_rounding_id,
            inv.date_invoice                        AS invoice_date,
            inv.date_due                            AS invoice_date_due,
            inv.incoterm_id                         AS invoice_incoterm_id,
            inv.origin                              AS invoice_origin,
            inv.partner_bank_id                     AS invoice_bank_partner_id,
            inv.reference                           AS invoice_payment_ref,
            CASE WHEN inv.state = 'cancel' THEN 'cancel' ELSE 'draft' END
                                                    AS state,
            inv.payment_term_id                     AS invoice_payment_term_id,
            inv.sent                                AS invoice_sent,
            inv.source_email                        AS invoice_source_email,
            inv.user_id                             AS invoice_user_id,
            inv.vendor_display_name                 AS invoice_partner_display_name,
            inv.journal_id,
            inv.name                                AS ref,
            inv.number                              AS name,
            inv.comment                             AS narration,
            inv.partner_id,
            inv.type
        FROM account_invoice inv
        WHERE inv.state NOT IN %s
          AND inv.move_id IS NULL
    """,
        [no_create_state],
    )
    for inv_vals in cr.dictfetchall():
        invoices[inv_vals["id"]] = inv_vals

    if invoices:

        # Before creating account moves, be sure that account_receivable_id and account_payable_id
        # properties of res_partners are valid (i.e with an account_id in the same company than the
        # property itself). If it's not the case, drop them.
        cr.execute(
            """
               DELETE FROM ir_property p
                USING account_account a
                WHERE a.id = replace(p.value_reference, 'account.account,', '')::integer
                  AND p.res_id IS NOT NULL
                  AND replace(p.res_id, 'res.partner,', '')::integer IN %s
                  AND p.name IN ('property_account_receivable_id', 'property_account_payable_id')
                  AND p.company_id != a.company_id
                  AND p.company_id IS NOT NULL
            RETURNING replace(p.res_id, 'res.partner,', '')
            """,
            [tuple(inv["partner_id"] for inv in invoices.values())],
        )

        if cr.rowcount:
            util.add_to_migration_reports(
                message="The following contacts have a problem with the company of their receivable and/or payable "
                "account. When accessed with a specific company using the multi-company dropdown menu, in the right of "
                "the top menu bar, these contacts use accounts belonging to another company then the currently used "
                "company. These invalid accounts have been unset from these contacts to be able to upgrade the "
                "accounting. To correct the accounts to use for these contacts, access the contact form and set the "
                "accounts for each company available in the dropdown multi-company menu. The contact ids are: %s."
                % ", ".join([str(id) for id, in cr.fetchall()]),
                category="Partner accounts",
            )

        # Manage account_invoice_line
        cr.execute(
            """
            SELECT
                inv_line.id,
                inv_line.name,
                inv_line.display_type,
                inv_line.sequence,
                inv_line.invoice_id,
                inv_line.uom_id                     AS product_uom_id,
                inv_line.product_id,
                CASE
                    WHEN inv_line.account_id IS NULL OR inv.company_id = account.company_id
                    THEN inv_line.account_id
                    ELSE (  SELECT COALESCE ((SELECT CASE
                                                     WHEN inv.type IN ('out_invoice', 'in_refund')
                                                        THEN j.default_credit_account_id
                                                        ELSE j.default_debit_account_id
                                                     END AS id
                                                FROM account_journal j
                                               WHERE j.id = inv.journal_id),
                                             (SELECT CASE
                                                     WHEN inv.type IN ('out_invoice', 'in_refund')
                                                        THEN j.default_credit_account_id
                                                        ELSE j.default_debit_account_id
                                                     END AS id
                                                FROM account_journal j
                                               WHERE j.company_id = inv.company_id
                                                 AND j.currency_id = inv.currency_id
                                                 AND j.type = CASE
                                                              WHEN inv.type IN ('out_invoice', 'out_refund')
                                                              THEN 'sale'
                                                              ELSE 'purchase'
                                                              END
                                                 AND (
                                                        inv.type IN ('out_invoice', 'in_refund')
                                                        AND j.default_credit_account_id IS NOT NULL
                                                         OR j.default_debit_account_id IS NOT NULL
                                                     )
                                               LIMIT 1),
                                             (SELECT a.id
                                                FROM account_account a
                                               WHERE a.company_id = inv.company_id
                                                 AND a.internal_type = account.internal_type
                                            ORDER BY (a.internal_group = account.internal_group) desc, id LIMIT 1))
                    )
                    END AS account_id,
                inv_line.price_unit,
                inv_line.quantity,
                inv_line.discount,
                array_remove(ARRAY_AGG(inv_line_tax.tax_id), NULL) AS tax_ids,
                inv_line.account_analytic_id        AS analytic_account_id,
                array_remove(ARRAY_AGG(tags.account_analytic_tag_id), NULL) AS analytic_tag_ids,
                inv_line.account_id                 AS original_account_id
            FROM account_invoice_line inv_line
            JOIN account_invoice inv ON inv.id = inv_line.invoice_id
            LEFT JOIN account_invoice_line_tax inv_line_tax ON inv_line_tax.invoice_line_id = inv_line.id
            LEFT JOIN account_analytic_tag_account_invoice_line_rel tags ON tags.account_invoice_line_id = inv_line.id
            LEFT JOIN account_account account ON account.id = inv_line.account_id
            WHERE inv_line.invoice_id IN %s
            GROUP BY
                inv_line.id,
                inv_line.name,
                inv_line.display_type,
                inv_line.sequence,
                inv_line.invoice_id,
                inv_line.uom_id,
                inv_line.product_id,
                inv_line.account_id,
                inv_line.price_unit,
                inv_line.quantity,
                inv_line.discount,
                inv_line.account_analytic_id,
                inv.company_id,
                inv.type,
                inv.journal_id,
                inv.currency_id,
                account.company_id,
                account.internal_type,
                account.internal_group
            ORDER BY inv_line.sequence, inv_line.id
        """,
            [tuple(invoices)],
        )

        updated_invoices = {}
        for line_vals in cr.dictfetchall():
            invoices[line_vals["invoice_id"]].setdefault("invoice_line_ids", []).append(line_vals)

            if line_vals["account_id"] != line_vals["original_account_id"]:
                updated_invoices.setdefault(line_vals["invoice_id"], []).append(line_vals["name"])

    # =======================================================================================
    # Create missing account_moves
    # =======================================================================================
    _logger.info("Create missing account moves")

    # Create account_move
    Move = env["account.move"].with_context(check_move_validity=False)
    created_moves = Move.browse()
    mappings = []
    for record_id, inv_vals in util.log_progress(invoices.items(), qualifier="invoices", logger=_logger):
        try:
            with util.savepoint(cr):
                created_move = Move.create(_convert_to_account_move_vals(inv_vals))
                created_moves |= created_move
                # Store link to newly created account_moves.
                mappings.append((created_move.id, record_id))
        except Exception:
            _logger.exception("Cannot create move from draft/cancel/custom invoice")
    cr.executemany("UPDATE account_invoice SET move_id=%s WHERE id=%s", mappings)

    # =======================================================================================
    # Post fix account_moves
    # =======================================================================================

    _compute_invoice_line_move_line_mapping(cr)

    if invoices and updated_invoices:
        mapping = {invoice_id: move_id for move_id, invoice_id in mappings}
        util.add_to_migration_reports(
            message="The following invoices had lines set with an account belonging to a company different than the "
            "invoice company. As these are draft or cancelled invoices, these lines have been reset with accounts "
            "from the right company. "
            "You should have a look at the lines of these invoices to make sure the accounts are set correctly: "
            "%s." % ", ".join("%s (%s)" % (mapping[id], ", ".join(lines)) for id, lines in updated_invoices.items()),
            category="Accounting",
        )

    # Fix lines having display_type != False.
    _logger.info("invoices: fix lines having display_type IS NOT NULL")
    if created_moves.ids:
        cr.execute(
            """
            UPDATE account_move_line aml_upd
               SET sequence=invoices.line_nb*10,
                   quantity=invoices.quantity,
                   price_unit=invoices.price_unit,
                   discount=invoices.discount,
                   price_subtotal=invoices.price_subtotal,
                   price_total=invoices.price_total
              FROM (
            SELECT invl.invoice_id,
                   invl.id,
                   invl.quantity,
                   invl.discount,
                   invl.price_unit,
                   invl.price_subtotal,
                   invl.price_total,
                   mapping.aml_id,
                   rank() over (PARTITION BY invl.invoice_id ORDER BY invl.invoice_id, invl.sequence, invl.id) as line_nb
            FROM account_invoice_line invl
      INNER JOIN account_invoice inv ON inv.id = invl.invoice_id
      INNER JOIN invl_aml_mapping mapping ON mapping.invl_id = invl.id
           WHERE inv.move_id NOT IN %s
             AND invl.display_type IS NULL
        ORDER BY invl.invoice_id, invl.sequence, invl.id) AS invoices
           WHERE aml_upd.id=invoices.aml_id
            """,
            [tuple(created_moves.ids)],
        )

    # Fix lines having display_type != False.
    if created_moves.ids:
        cr.execute(
            """
            SELECT invl.invoice_id,
                   invl.id,
                   invl.display_type,
                   invl.name,
                   inv.move_id,
                   inv.currency_id,
                   comp.currency_id as company_currency_id
            FROM account_invoice_line invl
      INNER JOIN account_invoice inv ON inv.id = invl.invoice_id
      INNER JOIN res_company comp ON comp.id=inv.company_id
             AND inv.move_id NOT IN %s
             AND invl.display_type IS NOT NULL
        ORDER BY invl.invoice_id, invl.sequence, invl.id
            """,
            [tuple(created_moves.ids)],
        )

        create_todo = []
        for res in cr.dictfetchall():
            create_todo.append(
                {
                    "move_id": res["move_id"],
                    "name": res["name"],
                    "currency_id": res["currency_id"] != res["company_currency_id"] and res["currency_id"] or False,
                    "display_type": res["display_type"],
                }
            )

        if create_todo:
            env["account.move.line"].create(create_todo)

    with util.disable_triggers(cr, "account_move"):
        # First un-exclude from invoice tab so that we can reuse exclude_from_invoice_tab field when computing amounts
        _logger.info("Un-exclude from invoice tab")
        cr.execute(
            """
            UPDATE account_move_line aml
               SET exclude_from_invoice_tab = FALSE
              FROM invl_aml_mapping m
             WHERE aml.id = m.aml_id
            """
        )
        cr.execute(
            """
            UPDATE account_move_line
               SET exclude_from_invoice_tab = FALSE
             WHERE account_id is null
               AND exclude_from_invoice_tab IS NULL
            """
        )

        _logger.info(
            "Fix amount_untaxed, amount_untaxed_signed, amount_tax, amount_tax_signed, "
            "amount_total, amount_total_signed, amount_residual, amount_residual_signed"
        )
        cr.execute(
            """
            SELECT COALESCE(SUM(balance), 0.0) as amount, COALESCE(SUM(amount_currency), 0.0) as amount_curr, move_id
              INTO TEMPORARY TABLE am_untaxed
              FROM account_move_line
             WHERE exclude_from_invoice_tab = false
          GROUP BY move_id
        """
        )
        cr.execute(
            """
            SELECT COALESCE(SUM(balance), 0.0) as amount, COALESCE(SUM(amount_currency), 0.0) as amount_curr, move_id
              INTO TEMPORARY TABLE am_tax
              FROM account_move_line
             WHERE tax_line_id IS NOT NULL
          GROUP BY move_id
        """
        )
        cr.execute(
            """
            SELECT COALESCE(SUM(balance), 0.0) as amount, COALESCE(SUM(amount_currency), 0.0) as amount_curr, move_id
              INTO TEMPORARY TABLE am_total
              FROM account_move_line
             WHERE account_internal_type NOT IN ('receivable', 'payable')
          GROUP BY move_id
        """
        )
        cr.execute(
            """
            SELECT COALESCE(SUM(amount_residual), 0.0) as amount,
                COALESCE(SUM(amount_residual_currency), 0.0) as amount_curr, move_id
              INTO TEMPORARY TABLE am_residual
              FROM account_move_line
             WHERE account_internal_type IN ('receivable', 'payable')
          GROUP BY move_id
        """
        )
        cr.execute("CREATE INDEX ON am_untaxed(move_id)")
        cr.execute("CREATE INDEX ON am_tax(move_id)")
        cr.execute("CREATE INDEX ON am_total(move_id)")
        cr.execute("CREATE INDEX ON am_residual(move_id)")

        cr.execute(
            """
            SELECT COALESCE(am_untaxed.amount,0) as untaxed_amount,COALESCE(am_untaxed.amount_curr,0) as untaxed_amount_curr,
                   COALESCE(am_tax.amount,0) as tax_amount,COALESCE(am_tax.amount_curr,0) as tax_amount_curr,
                   COALESCE(am_total.amount,0) as total_amount,COALESCE(am_total.amount_curr,0) as total_amount_curr,
                   COALESCE(am_residual.amount,0) as residual_amount,COALESCE(am_residual.amount_curr,0) as residual_amount_curr,
                   am.id
              INTO TABLE am_updatable_amounts
              FROM account_move am
         LEFT JOIN am_untaxed on am_untaxed.move_id=am.id
         LEFT JOIN am_tax on am_tax.move_id=am.id
         LEFT JOIN am_total on am_total.move_id=am.id
         LEFT JOIN am_residual on am_residual.move_id=am.id
        """
        )
        cr.execute("CREATE INDEX ON am_updatable_amounts(id)")

        _logger.info("Same currency as company")
        queries = {
            "single_currency_out_invoice": """
            -- ================ SINGLE-CURRENCY ================
            UPDATE account_move am
               SET amount_untaxed = am_updatable_amounts.untaxed_amount * (-1),
                   amount_untaxed_signed = am_updatable_amounts.untaxed_amount * (-1),
                   amount_tax = am_updatable_amounts.tax_amount * (-1),
                   amount_tax_signed = am_updatable_amounts.tax_amount * (-1),
                   amount_total = am_updatable_amounts.total_amount * (-1),
                   amount_total_signed = am_updatable_amounts.total_amount * (-1),
                   amount_residual = am_updatable_amounts.residual_amount,
                   amount_residual_signed = am_updatable_amounts.residual_amount
              FROM am_updatable_amounts, res_company c
             WHERE am.type IN ('out_invoice', 'out_receipt', 'in_refund')
               AND c.id = am.company_id
               AND am.currency_id = c.currency_id
               AND am_updatable_amounts.id=am.id
            """,
            "single_currency_in_invoice": """
            UPDATE account_move am
               SET amount_untaxed = am_updatable_amounts.untaxed_amount,
                   amount_untaxed_signed = am_updatable_amounts.untaxed_amount * (-1),
                   amount_tax = am_updatable_amounts.tax_amount,
                   amount_tax_signed =  am_updatable_amounts.tax_amount * (-1),
                   amount_total = am_updatable_amounts.total_amount,
                   amount_total_signed = am_updatable_amounts.total_amount * (-1),
                   amount_residual = am_updatable_amounts.residual_amount * (-1),
                   amount_residual_signed = am_updatable_amounts.residual_amount
              FROM am_updatable_amounts, res_company c
             WHERE am.type IN ('in_invoice', 'in_receipt', 'out_refund')
               AND c.id = am.company_id
               AND am.currency_id = c.currency_id
               AND am.id=am_updatable_amounts.id
            """,
            "single_currency_other": """
            UPDATE account_move am
               SET amount_untaxed = abs(am_updatable_amounts.untaxed_amount),
                   amount_untaxed_signed = abs(am_updatable_amounts.untaxed_amount),
                   amount_tax = abs(am_updatable_amounts.tax_amount),
                   amount_tax_signed = abs(am_updatable_amounts.tax_amount),
                   amount_total = abs(am_updatable_amounts.total_amount),
                   amount_total_signed = abs(am_updatable_amounts.total_amount),
                   amount_residual = abs(am_updatable_amounts.residual_amount),
                   amount_residual_signed = abs(am_updatable_amounts.residual_amount)
              FROM am_updatable_amounts, res_company c
             WHERE am.type = 'entry'
               AND c.id = am.company_id
               AND am.currency_id = c.currency_id
               AND am.id=am_updatable_amounts.id
            """,
            "multi_currency_out_invoice": """
            -- ================ MULTI-CURRENCIES ================
            UPDATE account_move am
               SET amount_untaxed = am_updatable_amounts.untaxed_amount_curr * (-1),
                   amount_untaxed_signed = am_updatable_amounts.untaxed_amount * (-1),
                   amount_tax = am_updatable_amounts.tax_amount_curr * (-1),
                   amount_tax_signed = am_updatable_amounts.tax_amount * (-1),
                   amount_total = am_updatable_amounts.total_amount_curr * (-1),
                   amount_total_signed = am_updatable_amounts.total_amount * (-1),
                   amount_residual = am_updatable_amounts.residual_amount_curr,
                   amount_residual_signed = am_updatable_amounts.residual_amount
              FROM am_updatable_amounts, res_company c
             WHERE am.type IN ('out_invoice', 'out_receipt', 'in_refund')
               AND c.id = am.company_id
               AND am.currency_id != c.currency_id
               AND am_updatable_amounts.id=am.id
            """,
            "multi_currency_in_invoice": """
            UPDATE account_move am
               SET amount_untaxed = am_updatable_amounts.untaxed_amount_curr,
                   amount_untaxed_signed = am_updatable_amounts.untaxed_amount * (-1),
                   amount_tax = am_updatable_amounts.tax_amount_curr,
                   amount_tax_signed = am_updatable_amounts.tax_amount * (-1),
                   amount_total = am_updatable_amounts.total_amount_curr,
                   amount_total_signed = am_updatable_amounts.total_amount * (-1),
                   amount_residual = am_updatable_amounts.residual_amount_curr * (-1),
                   amount_residual_signed = am_updatable_amounts.residual_amount
              FROM am_updatable_amounts, res_company c
             WHERE am.type IN ('in_invoice', 'in_receipt', 'out_refund')
               AND c.id = am.company_id
               AND am.currency_id != c.currency_id
               AND am.id=am_updatable_amounts.id
            """,
            "multi_currency_other": """
            UPDATE account_move am
               SET amount_untaxed = abs(am_updatable_amounts.untaxed_amount_curr),
                   amount_untaxed_signed = abs(am_updatable_amounts.untaxed_amount),
                   amount_tax = abs(am_updatable_amounts.tax_amount_curr),
                   amount_tax_signed = abs(am_updatable_amounts.tax_amount),
                   amount_total = abs(am_updatable_amounts.total_amount_curr),
                   amount_total_signed = abs(am_updatable_amounts.total_amount),
                   amount_residual = abs(am_updatable_amounts.residual_amount_curr),
                   amount_residual_signed = abs(am_updatable_amounts.residual_amount)
              FROM am_updatable_amounts, res_company c
             WHERE am.type = 'entry'
               AND c.id = am.company_id
               AND am.currency_id != c.currency_id
               AND am.id=am_updatable_amounts.id
        """,
        }

        util.parallel_execute(cr, queries.values())

        cr.execute(
            """
            WITH am_amounts AS ( SELECT am.id,
                                        SUM(aml.credit) as credit
                                   FROM account_move am
                                   JOIN account_move_line aml ON aml.move_id=am.id
                                  WHERE am.type='entry'
                               GROUP BY am.id)
            UPDATE account_move am
               SET amount_total_signed=am_amounts.credit
              FROM am_amounts
             WHERE am_amounts.id=am.id
            """
        )

        _logger.info("Fix invoice_payment_state.")
        # A move is paid if all its payable/receivable lines (at least 1) are reconciled
        cr.execute(
            """
            UPDATE account_move am
               SET invoice_payment_state = CASE WHEN sub.all_reconciled THEN 'paid' ELSE 'not_paid' END
              FROM (
                   SELECT move_id, EVERY(reconciled) all_reconciled
                     FROM account_move_line
                    WHERE account_internal_type IN ('receivable', 'payable')
                    GROUP BY move_id
              ) AS sub
             WHERE am.id = sub.move_id
        """
        )
        cr.execute("UPDATE account_move SET invoice_payment_state = 'not_paid' WHERE invoice_payment_state IS NULL")

        # The two queries below are separate for performance reason. (more details in the PR)
        cr.execute(
            """
            UPDATE account_move am
            SET invoice_payment_state = 'in_payment'
            WHERE am.invoice_payment_state = 'paid'
            AND am.id IN (
                SELECT move.id
                FROM account_move move
                JOIN account_move_line line ON line.move_id = move.id
                JOIN account_partial_reconcile part ON part.debit_move_id = line.id OR part.credit_move_id = line.id
                /*slight variation with next query in next join*/
                JOIN account_move_line rec_line ON (rec_line.id = part.debit_move_id AND line.id = part.credit_move_id)
                JOIN account_payment payment ON payment.id = rec_line.payment_id
                JOIN account_journal journal ON journal.id = rec_line.journal_id
                WHERE payment.state IN ('posted', 'sent')
                AND journal.post_at_bank_rec IS TRUE
            )
        """
        )
        cr.execute(
            """
            UPDATE account_move am
            SET invoice_payment_state = 'in_payment'
            WHERE am.invoice_payment_state = 'paid'
            AND am.id IN (
                SELECT move.id
                FROM account_move move
                JOIN account_move_line line ON line.move_id = move.id
                JOIN account_partial_reconcile part ON part.debit_move_id = line.id OR part.credit_move_id = line.id
                /*slight variation with previous query in next join*/
                JOIN account_move_line rec_line ON (rec_line.id = part.credit_move_id AND line.id = part.debit_move_id)
                JOIN account_payment payment ON payment.id = rec_line.payment_id
                JOIN account_journal journal ON journal.id = rec_line.journal_id
                WHERE payment.state IN ('posted', 'sent')
                AND journal.post_at_bank_rec IS TRUE
            )
        """
        )

        _logger.info("Migrate refund_invoice_id => reversed_entry_id")
        cr.execute(
            """
            UPDATE account_move am
               SET reversed_entry_id = refund.move_id
              FROM account_invoice inv
        INNER JOIN account_invoice refund ON refund.id = inv.refund_invoice_id
             WHERE am.id=inv.move_id
        """
        )

        _logger.info("Migrate multiple important fields from account_invoice to account_move.")
        cr.execute(
            """
            UPDATE account_move am
               SET message_main_attachment_id = inv.message_main_attachment_id,
                   partner_id = inv.partner_id
              FROM account_invoice inv
             WHERE am.id = inv.move_id
            """
        )

        _logger.info("Un-exclude from invoice tab")
        cr.execute(
            """
            UPDATE account_move_line aml
               SET exclude_from_invoice_tab = FALSE
              FROM invl_aml_mapping m
             WHERE aml.id = m.aml_id
            """
        )
        cr.execute(
            """
            UPDATE account_move_line
               SET exclude_from_invoice_tab = FALSE
             WHERE account_id is null
               AND exclude_from_invoice_tab IS NULL
            """
        )


def migrate(cr, version):
    cr.execute("CREATE INDEX ON account_tax(company_id) WHERE (amount_type)::text <> 'percent'::text")
    cr.execute("CREATE INDEX ON account_tax(company_id) WHERE (amount_type)::text = 'percent'::text")
    cr.execute("REINDEX TABLE account_tax")
    with no_fiscal_lock(cr):
        if util.ENVIRON["account_voucher_installed"]:
            migrate_voucher_lines(cr)
        migrate_invoice_lines(cr)
