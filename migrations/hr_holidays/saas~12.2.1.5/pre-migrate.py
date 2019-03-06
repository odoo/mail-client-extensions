# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.rename_field(cr, "hr.employee", "is_absent_today", "is_absent")

    util.remove_record(cr, "hr_holidays.open_company_allocation")
    util.remove_record(cr, "hr_holidays.menu_open_company_allocation")
