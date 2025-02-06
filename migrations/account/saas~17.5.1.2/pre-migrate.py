from odoo.tools import SQL

from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "res_company", "sale_lock_date", "date")
    util.create_column(cr, "res_company", "purchase_lock_date", "date")
    cr.execute(
        """
        UPDATE res_company c
           SET sale_lock_date = c.period_lock_date,
               purchase_lock_date = c.period_lock_date
         WHERE c.period_lock_date IS NOT NULL
        """,
    )
    util.remove_field(cr, "res.company", "period_lock_date")
    util.remove_field(cr, "res.company", "max_tax_lock_date")

    util.rename_field(cr, "account.move", "made_sequence_hole", "made_sequence_gap")
    util.create_column(cr, "account_move", "made_sequence_gap", "bool")

    query = """
        WITH to_update AS (
            SELECT this.id
              FROM account_move this
         LEFT JOIN account_move other ON this.journal_id = other.journal_id
                                     AND this.sequence_prefix = other.sequence_prefix
                                     AND this.sequence_number = other.sequence_number + 1
             WHERE other.id IS NULL
               AND this.sequence_number != 1
               AND this.name != '/'
               AND {parallel_filter}
        )
        UPDATE account_move
           SET made_sequence_gap = TRUE
          FROM to_update
         WHERE account_move.id = to_update.id
    """
    util.explode_execute(cr, query, table="account_move", alias="this")
    cr.execute("DROP INDEX IF EXISTS account_move_sequence_index3")
    util.rename_field(cr, "account.move", "reversal_move_id", "reversal_move_ids")
    util.remove_record(cr, "account.invoice_send")

    # Autopost bills
    util.create_column(cr, "account_move", "is_manually_modified", "bool", default=True)
    util.create_column(cr, "res_partner", "autopost_bills", "varchar", default="ask")
    util.create_column(cr, "res_company", "autopost_bills", "bool", default=True)

    util.create_column(cr, "account_move", "preferred_payment_method_line_id", "int4")
    if util.column_exists(cr, "account_move", "preferred_payment_method_id"):
        # Create a mapping for payment_method and a payment method line
        query = """
            WITH pay_lines AS (
                SELECT l.payment_method_id,
                       j.company_id,
                       min(l.id) AS payment_method_line_id
                  FROM account_payment_method_line l
                  JOIN account_journal j
                    ON j.id = l.journal_id
              GROUP BY l.payment_method_id, j.company_id
            )
          UPDATE account_move am
             SET preferred_payment_method_line_id = pl.payment_method_line_id
            FROM pay_lines pl
           WHERE am.preferred_payment_method_id = pl.payment_method_id
             AND am.company_id = pl.company_id
        """
        util.explode_execute(cr, query, table="account_move", alias="am")

    # Share accounts between companies
    # 1. Populate code_store with account codes
    util.create_column(cr, "account_account", "code_store", "jsonb")
    cr.execute(
        SQL(
            """
            UPDATE account_account
               SET code_store = jsonb_build_object(SPLIT_PART(res_company.parent_path, '/', 1), account_account.code)
              FROM res_company
             WHERE res_company.id = account_account.company_id
            """
        )
    )

    # 2. Create and populate account_account_res_company_rel
    util.create_m2m(cr, "account_account_res_company_rel", "account_account", "res_company")
    cr.execute("""
        INSERT INTO account_account_res_company_rel (account_account_id, res_company_id)
             SELECT id AS account_account_id,
                    company_id AS res_company_id
               FROM account_account
    """)
    util.rename_field(cr, "account.account", "company_id", "company_ids")
    util.remove_column(cr, "account_account", "company_ids")

    # 3. Misc column/field changes
    util.make_field_non_stored(cr, "account.account", "group_id", selectable=False)
    util.make_field_non_stored(cr, "account.account", "root_id", selectable=True)
    util.make_field_non_stored(cr, "account.move.line", "account_root_id", selectable=True)
    cr.execute('DROP VIEW IF EXISTS "account_root" CASCADE')
    util.remove_field(cr, "account.root", "company_id")
    util.remove_record(cr, "account.account_root_comp_rule")
    util.remove_field(cr, "account.cash.rounding", "company_id")

    util.remove_model(cr, "account.unreconcile")

    util.invert_boolean_field(cr, "account.move", "to_check", "checked")
    cr.execute("ALTER INDEX IF EXISTS account_move_to_check_idx RENAME TO account_move_checked_idx")

    util.create_column(cr, "account_move", "amount_untaxed_in_currency_signed", "numeric")
    query_amount_untaxed = """
        UPDATE account_move
           SET amount_untaxed_in_currency_signed = amount_untaxed *
     CASE WHEN move_type IN ('entry', 'in_invoice', 'out_refund', 'in_receipt')
          THEN -1 ELSE 1 END
    """
    util.explode_execute(cr, query_amount_untaxed, table="account_move")

    util.remove_field(cr, "account.move.line", "blocked")

    # `code` is always 6 digits long, they get appended zeroes otherwise
    # the fix must be done here, because by the time when l10n_in is loaded
    # the xmlids would already be there:
    # https://github.com/odoo/enterprise/blob/517983ae/account_accountant/__init__.py#L30
    if util.module_installed(cr, "l10n_in"):
        query = """
          UPDATE ir_model_data d
             SET name = concat(c.id, '_p10058')
            FROM account_account a,
                 res_company c
            JOIN res_country n
              ON n.id = c.account_fiscal_country_id
           WHERE d.model = 'account.account'
             AND d.res_id = a.id
             AND d.name = concat(c.id, '_p10054')
             AND n.code = 'IN'
             AND a.code = '100580'
        """
        cr.execute(query)
