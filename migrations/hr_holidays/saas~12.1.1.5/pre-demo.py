# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    renames = """
        hr_holidays_employee1_allocation_cl
        hr_holidays_employee1_int_tour
        hr_holidays_employee1_allocation_hl
        hr_holidays_employee1_vc
        hr_holidays_employee1_cl
        hr_holidays_employee1_sl
    """
    for name in util.splitlines(renames):
        to = name.replace("employee1_", "")
        util.rename_xmlid(cr, f"hr_holidays.{name}", f"hr_holidays.{to}")
