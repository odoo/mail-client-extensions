# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "res.config.settings", "pos_employee_ids", "pos_basic_employee_ids")
    util.rename_field(cr, "pos.config", "employee_ids", "basic_employee_ids")

    # rename m2m hr_employee_pos_config_rel table to pos_hr_basic_employee_hr_employee
    cr.execute(
        """
        ALTER TABLE hr_employee_pos_config_rel
          RENAME TO pos_hr_basic_employee_hr_employee
    """
    )
