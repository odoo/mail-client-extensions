# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.update_record_from_xml(cr, "l10n_be_hr_payroll_fleet.rule_parameter_value_fuel_coefficient_2016")
    util.update_record_from_xml(cr, "l10n_be_hr_payroll_fleet.rule_parameter_tax_deduction_fuel_2020")
