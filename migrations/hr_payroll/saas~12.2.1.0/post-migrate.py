# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute("UPDATE hr_payroll_structure SET report_id = %s",
               [util.ref(cr, "hr_payroll.action_report_payslip")])
