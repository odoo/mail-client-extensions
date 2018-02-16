# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_record(cr, 'hr_payroll.action_view_hr_payroll_structure_tree')
    util.remove_record(cr, 'hr_payroll.menu_hr_payroll_structure_tree')
