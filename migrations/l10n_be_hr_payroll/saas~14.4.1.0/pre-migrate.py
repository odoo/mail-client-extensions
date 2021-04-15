# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.delete_unused(cr, "l10n_be_hr_payroll.cp200_employees_salary_reim_travel")
    util.delete_unused(cr, "l10n_be_hr_payroll.cp200_pfi_reim_travel")
    util.delete_unused(cr, "l10n_be_hr_payroll.cp200_employees_double_holiday_reim_travel")
    util.remove_field(cr, "hr.contract", "others_reimbursed_amount")

    util.remove_model(cr, "hr.payroll.281.base.wizard")
    util.remove_model(cr, "hr.payroll.281.10.wizard")
    util.remove_model(cr, "hr.payroll.281.45.wizard")
    util.remove_model(cr, "l10n.be.withholding.tax.exemption")
    util.remove_model(cr, "l10n.be.withholding.tax.exemption.line")
    util.remove_model(cr, "l10n.be.withholding.tax.ip.declaration")
