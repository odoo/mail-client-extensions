from odoo.upgrade import util


def migrate(cr, version):
    for deferred_type, xml_id in (["expense", "a490"], ["revenue", "a493"]):
        query = util.format_query(
            cr,
            """
            UPDATE res_company company
               SET {}  = (
                    SELECT account.id
                      FROM account_account account
                      JOIN ir_model_data imd
                        ON imd.model = 'account.account' AND imd.res_id = account.id
                     WHERE account.company_id = company.id
                       AND imd.name = account.company_id || '_' || %s
                     LIMIT 1
            )
             WHERE company.chart_template = 'be'
            """,
            f"deferred_{deferred_type}_account_id",
        )
        cr.execute(query, [xml_id])
