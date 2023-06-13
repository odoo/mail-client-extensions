# -*- coding: utf-8 -*-
from odoo.upgrade import util


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

    util.remove_field(cr, "hr.applicant", "access_token")
    util.remove_field(cr, "hr.applicant", "access_token_end_date")
    util.remove_field(cr, "hr.employee", "salary_simulator_link_end_validity")
    util.remove_field(cr, "generate.simulation.link", "url")
