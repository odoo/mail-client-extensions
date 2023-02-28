# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.move_field_to_module(cr, "hr.employee", "resident_bool", "l10n_be_hr_payroll", "hr_payroll")
    util.move_field_to_module(cr, "res.users", "resident_bool", "l10n_be_hr_payroll", "hr_payroll")
    util.rename_field(cr, "hr.employee", "resident_bool", "is_non_resident")
    util.rename_field(cr, "res.users", "resident_bool", "is_non_resident")

    util.move_field_to_module(cr, "hr.employee", "l10n_lt_is_non_resident", "l10n_lt_hr_payroll", "hr_payroll")
    util.move_field_to_module(cr, "res.users", "l10n_lt_is_non_resident", "l10n_lt_hr_payroll", "hr_payroll")
    util.rename_field(cr, "hr.employee", "l10n_lt_is_non_resident", "is_non_resident")
    util.rename_field(cr, "res.users", "l10n_lt_is_non_resident", "is_non_resident")
