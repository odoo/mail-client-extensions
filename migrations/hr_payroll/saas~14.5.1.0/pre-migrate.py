# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.move_field_to_module(cr, "hr.employee", "mobile_invoice", "l10n_be_hr_contract_salary", "hr_payroll")
    util.move_field_to_module(cr, "hr.employee", "sim_card", "l10n_be_hr_contract_salary", "hr_payroll")
    util.move_field_to_module(cr, "hr.employee", "internet_invoice", "l10n_be_hr_contract_salary", "hr_payroll")
