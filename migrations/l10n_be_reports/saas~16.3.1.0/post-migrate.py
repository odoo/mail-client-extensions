# -*- coding: utf-8 -*-


def migrate(cr, version):
    for deferred_type, xml_id in (["expense", "a490"], ["revenue", "a493"]):
        cr.execute(
            f"""
            UPDATE res_company company
               SET deferred_{deferred_type}_account_id  = (
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
            (xml_id,),
        )
