import logging
import os
from ast import literal_eval

from odoo.upgrade import util

ODOO_MIG_16_MIGRATE_CUSTOM_FINANCIAL_REPORTS = util.str2bool(
    os.getenv("ODOO_MIG_16_MIGRATE_CUSTOM_FINANCIAL_REPORTS"), ""
)


def migrate(cr, version):
    if not (ODOO_MIG_16_MIGRATE_CUSTOM_FINANCIAL_REPORTS or util.on_CI()) or not util.column_exists(
        cr, "account_report_line", "v15_fin_line_id"
    ):
        return  # nosemgrep: no-early-return

    _logger = logging.getLogger(__name__)

    # constant regexes
    DOMAIN_EXPR_REGEX = r"-?sum(?:_if_(?:pos|neg)(?:_groupby)?)?"

    # There are 2 cases under which we need to migrate extra lines:
    #   1. Migrated aggregation formulas make use of lines that used to be standard in v15 and are no longer there in Odoo 16.
    #   2. Migrated aggregation formulas make use of lines with report_id = NULL
    # In both cases, they are detected with the following query and migrated later on
    cr.execute(
        r"""
        WITH codes_by_id AS (
            SELECT
                REGEXP_SPLIT_TO_TABLE(
                    REGEXP_REPLACE(
                        are.formula,
                        %s,
                        ' ',
                        'g'
                    ),
                    '[\s\+\*\-/]+'
                ) AS code,
                are.report_line_id
              FROM account_report_expression are
              JOIN account_report_line arl
                ON arl.id = are.report_line_id
               AND arl.v15_fin_line_id IS NOT NULL
             WHERE are.engine = 'aggregation'
        ),
        codes_to_migrate_by_id AS (
            SELECT code, report_line_id
              FROM codes_by_id c
             WHERE NOT EXISTS (SELECT 1 FROM account_report_line WHERE code = c.code)
               AND c.code != ''
        )
        SELECT report_line_id, ARRAY_AGG(code)
          FROM codes_to_migrate_by_id
         GROUP BY report_line_id
        """,
        [rf"(?:^-|\.balance|\(|\)|{DOMAIN_EXPR_REGEX}|sum_children)"],
    )

    for report_line_id, codes_to_migrate in cr.fetchall():
        migrated_codes = set()

        while codes_to_migrate:
            code = codes_to_migrate.pop()

            # migrate term's formula to a subexpression of the faulty expression
            cr.execute(
                r"""
                INSERT INTO account_report_expression (
                    create_uid, write_uid, create_date, write_date, report_line_id,
                    label, date_scope, figure_type, green_on_positive, auditable,
                    engine,
                    formula,
                    subformula
                )
                SELECT afhrl.create_uid, afhrl.write_uid, afhrl.create_date, NOW(), %(report_line_id)s,
                       LOWER(afhrl.code), afhrl.special_date_changer, afhrl.figure_type, afhrl.green_on_positive, True,
                       -- engine
                          CASE
                                WHEN afhrl.formulas ~ %(re)s THEN 'domain'
                                ELSE 'aggregation'
                          END,
                       -- formula
                          CASE
                                WHEN afhrl.formulas ~ %(re)s THEN afhrl.domain
                                ELSE REGEXP_REPLACE(afhrl.formulas, '(\w+)', '\1.balance', 'g')
                          END,
                       -- subformula
                          CASE
                                WHEN afhrl.formulas ~ %(re)s THEN afhrl.formulas
                                ELSE 'cross_report'
                          END
                  FROM ___upgrade_afhrl afhrl
                 WHERE afhrl.code = %(code)s
             RETURNING id
                """,
                {"report_line_id": report_line_id, "code": code, "re": f"^{DOMAIN_EXPR_REGEX}$"},
                [report_line_id, code],
            )

            if not cr.rowcount:
                # no expression was added because of the `afhrl.code = %s` check, thus the code doesn't exist in the origin db
                # either something was already wrong or the formula parsing ignores some corner case.
                _logger.error(
                    "term code `%s` was not found in the source db. Some reports may be affected.",
                    code,
                )
                continue

            (subexp_id,) = cr.fetchone()

            # replace $term_code.balance in formula with $line_code.$term_code
            cr.execute(
                r"""
                UPDATE account_report_expression are
                   SET formula = REGEXP_REPLACE(
                           are.formula,
                           '(?<=\s|^)' || %s || '\.balance',
                           arl.code || '.' || LOWER(%s),
                           'g'
                       )
                  FROM account_report_line arl
                 WHERE are.report_line_id = arl.id
                   AND arl.id = %s
                """,
                [code, code, report_line_id],
            )

            # migrated code's formula might contain more codes to migrate separately
            cr.execute(
                r"""
                WITH new_codes AS (
                    SELECT
                        REGEXP_SPLIT_TO_TABLE(
                            REGEXP_REPLACE(
                                are.formula,
                                %s,
                                '',
                                'g'
                            ),
                            '[\s\+\*\-/]+'
                        ) AS code
                      FROM account_report_expression are
                     WHERE are.id = %s
                       AND are.engine = 'aggregation'
                )
                SELECT code
                  FROM new_codes c
                 WHERE NOT EXISTS (SELECT 1 FROM account_report_line WHERE code = c.code)
                   AND code IS NOT NULL
                 GROUP BY code
                """,
                [rf"(?:^-|\.balance|\(|\)|{DOMAIN_EXPR_REGEX})", subexp_id],
            )

            # keep track of already migrated codes for the current expression…
            migrated_codes.add(code)
            codes_to_migrate.extend(r[0] for r in cr.fetchall() if r[0] not in migrated_codes)

    util.remove_column(cr, "account_report_line", "v15_fin_line_id")

    cr.execute("DROP TABLE ___upgrade_afhrl")

    # some terms may include both aggregators and term codes - split them into different subexpressions
    # also be aware that, in such mixed formulas, the aggregators will have an extra '.balance' that needs to be discarded
    cr.execute(
        """
        INSERT INTO account_report_expression (
            create_uid, write_uid, create_date, write_date, report_line_id,
            label, engine, formula, subformula,
            date_scope, figure_type, green_on_positive, auditable
        )
        SELECT are.create_uid, are.write_uid, are.create_date, NOW(), arl.id,
               'agg', 'domain', arl.v15_domain, SUBSTRING(are.formula FROM %s),
               are.date_scope, are.figure_type, are.green_on_positive, are.auditable
          FROM account_report_expression are
          JOIN account_report_line arl
            ON arl.id = are.report_line_id
         WHERE engine = 'aggregation'
           AND formula ~ %s
        """,
        [f"({DOMAIN_EXPR_REGEX})", rf"(?<=\W|^){DOMAIN_EXPR_REGEX}\.balance(?=\W|$)"],
    )

    util.remove_column(cr, "account_report_line", "v15_domain")

    cr.execute(
        """
        UPDATE account_report_expression are
           SET formula = REGEXP_REPLACE(are.formula, %s, arl.code || '.agg')
          FROM account_report_line arl
         WHERE are.engine = 'aggregation'
           AND are.formula ~ %s
           AND are.report_line_id = arl.id
        """,
        [rf"{DOMAIN_EXPR_REGEX}\.balance", rf"(?<=\W|^){DOMAIN_EXPR_REGEX}\.balance(?=\W|$)"],
    )

    # Given that Odoo 16 no longer supports sum_if_(pos|neg)_groupby, expressions relying on them must have their domain adapted
    # For an example, see _prepare_test_custom_fin_report_migrated in test_16_reportalypse.py
    cr.execute(
        """
        SELECT id,
               subformula LIKE '%pos%' AS debit_flag,
               subformula LIKE '-%' as neg_flag,
               formula AS domain
          FROM account_report_expression
         WHERE subformula ~ '-?sum_if_(?:pos|neg)_groupby'
        """
    )

    for id, debit, neg_sign, d in cr.fetchall():
        domain = literal_eval(d)

        patterns = []
        antipatterns = []
        target = patterns
        for token in domain:
            if isinstance(token, tuple):  # e.g. ('account_id.code', '=like', '40%')
                if len(token) != 3:
                    raise ValueError(f"Domain's element length is not 3: {token}")
                if not token[0] == "account_id.code":
                    raise ValueError(f"Domain contains condition on {token[0]} field instead of 'account_id.code'")

                t = token[2].replace("%", "")
                if not t.isnumeric():
                    raise ValueError(f"Domain assumption violated: Unrecognized, non-numeric token = {token}")

                if token[1] == "=like":
                    target.append(t)
                elif token[1] == "not like":
                    antipatterns.append(t)
                else:
                    raise ValueError(f"Domain contains unknown comparator: {token[1]}")
            elif token == "!":
                if target is antipatterns:
                    raise ValueError(f"Multiple '!'s found in expression with id = {id}, in domain = {domain}")
                target = antipatterns
            elif token != "|":
                raise ValueError(f"Unknown token = {token}, in domain {domain}")

        # new_formula defined as per Odoo 16 specifications:
        # https://github.com/odoo/enterprise/blob/ee3fa2f85d11e529613e749d7bfe6640cc0df02d/account_reports/models/account_report.py#L2798
        new_formula, sum_sign = ("-", " - ") if neg_sign else ("", " + ")
        letter_code = "D" if debit else "C"
        for pattern in patterns:
            new_formula += pattern
            antipattern = ",".join(filter(lambda x: x.startswith(pattern), antipatterns))
            if antipattern:
                new_formula += r"\(" + antipattern + ")"
            new_formula += letter_code + sum_sign
        new_formula = new_formula.rstrip(" +-")

        cr.execute(
            """
            UPDATE account_report_expression
               SET engine = 'account_codes',
                   subformula = NULL,
                   formula = %s
             WHERE id = %s
            """,
            [new_formula, id],
        )
