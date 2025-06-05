from itertools import product

from odoo.upgrade import util


def migrate(cr, version):
    """
    This upgrade script assigns partner_id to unreconciled bank statement lines
    The logic is equivalent to `_retrieve_partner` of account.bank.statement.line model
    """
    partner_by_account_number_query = """
            WITH line_partner AS (
              SELECT l.id, (ARRAY_AGG(p.id ORDER BY p.active IS TRUE DESC, p.id))[1] AS partner_id
                FROM account_bank_statement_line l
                JOIN res_company c
                  ON c.id = l.company_id
                JOIN res_partner_bank b
                  ON b.sanitized_acc_number ILIKE '%' || NULLIF(regexp_replace(l.account_number, '\\W+', ''), '') || '%'
                JOIN res_partner p
                  ON p.id = b.partner_id
               WHERE l.partner_id IS NULL
                 AND l.is_reconciled = FALSE
                 AND {{parallel_filter}}
                 AND {company_condition}
            GROUP BY l.id
              HAVING COUNT(DISTINCT p.id) = 1
                  OR COUNT(DISTINCT p.id) FILTER (WHERE p.active = TRUE) = 1
        ) UPDATE account_bank_statement_line line
             SET partner_id = line_partner.partner_id
            FROM line_partner
           WHERE line_partner.id = line.id
    """
    company_conditions = [
        "b.company_id::TEXT = ANY(STRING_TO_ARRAY(c.parent_path, '/'))",
        "b.company_id IS NULL",
    ]
    for company_condition in company_conditions:
        query = util.format_query(
            cr,
            partner_by_account_number_query,
            company_condition=util.SQLStr(company_condition),
        )
        util.explode_execute(cr, query, table="account_bank_statement_line", alias="l")

    partner_by_complete_name_query = """
             WITH line_partner AS (
               SELECT l.id, MIN(p.id) AS partner_id
                 FROM account_bank_statement_line l
                 JOIN res_company c
                   ON c.id = l.company_id
                 JOIN res_partner p
                   ON {on_condition}
                WHERE l.partner_id IS NULL
                  AND l.is_reconciled = FALSE
                  AND {{parallel_filter}}
                  AND COALESCE(l.partner_name, '') <> ''
                  AND p.parent_id IS NULL
                  AND {and_condition}
             GROUP BY l.id
               HAVING COUNT(*) = 1
         ) UPDATE account_bank_statement_line line
              SET partner_id = line_partner.partner_id
             FROM line_partner
            WHERE line_partner.id = line.id
    """

    on_conditions = [
        "LOWER(p.complete_name) = LOWER(l.partner_name)",
        "p.complete_name ILIKE '%' || l.partner_name || '%'",
    ]
    and_conditions = [
        "p.company_id::TEXT = ANY(STRING_TO_ARRAY(c.parent_path, '/'))",
        "p.company_id IS NULL",
    ]
    for on_condition, and_condition in product(on_conditions, and_conditions):
        query = util.format_query(
            cr,
            partner_by_complete_name_query,
            on_condition=util.SQLStr(on_condition),
            and_condition=util.SQLStr(and_condition),
        )
        util.explode_execute(cr, query, table="account_bank_statement_line", alias="l")

    partner_by_latest_statement_lines_query = """
             WITH line_partner_ranked AS (
               SELECT l1.id, l2.partner_id, ROW_NUMBER() OVER (PARTITION BY l1.id ORDER BY l2.id DESC) AS rn
                 FROM account_bank_statement_line l1
                 JOIN account_bank_statement_line l2
                   ON (l1.company_id IS NOT DISTINCT FROM l2.company_id OR l2.company_id IS NULL)
                  AND l1.partner_name = l2.partner_name
                WHERE l1.partner_id IS NULL
                  AND l1.is_reconciled = FALSE
                  AND {parallel_filter}
                  AND COALESCE(l1.partner_name, '') <> ''
                  AND l2.is_reconciled = TRUE
         ), line_partner AS (
               SELECT id, MIN(partner_id) AS partner_id
                 FROM line_partner_ranked
                WHERE rn <= 3
             GROUP BY id
               HAVING COUNT(DISTINCT partner_id) = 1
         ) UPDATE account_bank_statement_line line
              SET partner_id = line_partner.partner_id
             FROM line_partner
            WHERE line_partner.id = line.id
    """
    util.explode_execute(cr, partner_by_latest_statement_lines_query, table="account_bank_statement_line", alias="l1")
