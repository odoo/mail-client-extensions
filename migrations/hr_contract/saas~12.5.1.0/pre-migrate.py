# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "hr_contract", "kanban_state", "varchar")
    cr.execute(
        """
        UPDATE hr_contract
           SET kanban_state = CASE state WHEN 'incoming' THEN 'done'
                                         WHEN 'pending'  THEN 'blocked'
                                                         ELSE 'normal'
                               END
    """
    )
    cr.execute("UPDATE hr_contract SET state = 'draft' WHERE state = 'incoming'")
    cr.execute("UPDATE hr_contract SET state = 'open' WHERE state = 'pending'")

    cr.execute(
        """
        UPDATE hr_contract c
           SET company_id = e.company_id
          FROM hr_employee e
         WHERE e.id = c.employee_id
           AND c.company_id IS NULL
    """
    )

    util.create_column(cr, "hr_employee", "contract_warning", "boolean")
    cr.execute(
        """
        WITH warns AS (
            SELECT e.id
              FROM hr_employee e
         LEFT JOIN hr_contract c ON c.id = e.contract_id
            -- We known that *all* contracts has a `kanban_state` set (just above)
            -- So, the `coalesce` handle the case of employees without contract
             WHERE COALESCE(c.kanban_state, 'blocked') = 'blocked'
                OR c.state != 'open'
        )
        UPDATE hr_employee
           SET contract_warning = true
         WHERE id IN (SELECT id FROM warns)
    """
    )
