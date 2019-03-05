# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "res_users", "employee_id", "int4")
    cr.execute(
        """
        UPDATE res_users u
           SET employee_id = e.id
          FROM hr_employee e
         WHERE e.user_id = u.id
           AND e.company_id = u.company_id
    """
    )
