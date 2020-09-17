# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    # Take company_id on resource_calendar if exists
    cr.execute(
        """
            UPDATE hr_employee e
               SET company_id = rc.company_id
              FROM resource_calendar rc
             WHERE e.company_id IS NULL
               AND rc.id = e.resource_calendar_id
        """
    )

    # Fallback on the company_id of the hr_contrat based on the latest start_date linked to the employee_id
    if util.table_exists(cr, "hr_contract"):
        cr.execute(
            """
                WITH last_contracts AS (
                    SELECT employee_id, (array_agg(company_id ORDER BY date_start desc))[1] AS company_id
                        FROM hr_contract
                    GROUP BY employee_id
                )
                UPDATE hr_employee e
                      SET company_id = c.company_id
                    FROM last_contracts c
                  WHERE c.employee_id = e.id
                      AND e.company_id IS NULL
            """
        )
