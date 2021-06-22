# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):

    # Remove the unique constraint (user_id, company_id) temporary
    cr.execute("ALTER TABLE hr_employee DROP CONSTRAINT IF EXISTS hr_employee_user_uniq")

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

    # Deduplicate employees and reset the unique constraint
    cr.execute(
        """
              SELECT array_agg(id ORDER BY id)
                FROM hr_employee
               WHERE user_id IS NOT NULL
                 AND company_id IS NOT NULL
            GROUP BY user_id, company_id
              HAVING COUNT(id) > 1
        """
    )
    for (dupes,) in cr.fetchall():
        keep = dupes.pop(0)
        idmap = {d: keep for d in dupes}
        util.replace_record_references_batch(cr, idmap, "hr.employee")
        for dup in dupes:
            util.remove_record(cr, ("hr.employee", dup))
    cr.execute("ALTER TABLE hr_employee ADD CONSTRAINT hr_employee_user_uniq UNIQUE(user_id, company_id)")
