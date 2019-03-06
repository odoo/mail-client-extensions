# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_field(cr, "hr.employee", "manager")
    util.create_column(cr, "hr_employee", "contract_id", "int4")
    cr.execute(
        """
        WITH contracts AS (
            SELECT employee_id,
                   (array_agg(id ORDER BY date_start DESC))[1] AS id
              FROM hr_contract
          GROUP BY employee_id
        )
        UPDATE hr_employee e
           SET contract_id = c.id
          FROM contracts c
         WHERE c.employee_id = e.id
    """
    )
