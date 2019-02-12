# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_model(cr, "report.l10n_in_hr_payroll.report_payslipdetails")
