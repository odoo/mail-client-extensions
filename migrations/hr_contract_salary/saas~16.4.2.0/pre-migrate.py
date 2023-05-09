# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute(
        r"""
            WITH templates AS (
                SELECT sign_template_id as id
                  FROM hr_contract
                 WHERE sign_template_id IS NOT NULL
                 UNION
                 SELECT contract_update_template_id as id
                   FROM hr_contract
                  WHERE contract_update_template_id IS NOT NULL
            )
            UPDATE sign_item i
               SET name = replace(i.name, 'employee_id.', 'employee_id.private_')
              FROM templates t
             WHERE t.id = i.template_id
               AND i.name ~ '^employee_id\.(street|street2|city|zip|state_id|country_id|email|phone)\y'
            """
    )
