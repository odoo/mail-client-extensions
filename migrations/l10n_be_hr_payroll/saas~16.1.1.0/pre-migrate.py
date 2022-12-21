# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.rename_xmlid(cr, "l10n_be_hr_payroll.hr_payslip_run_view_tree", "l10n_be_hr_payroll.hr_payslip_run_view_form")
