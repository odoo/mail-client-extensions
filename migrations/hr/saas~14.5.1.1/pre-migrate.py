# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.move_field_to_module(cr, "hr.employee", "id_card", "l10n_be_hr_contract_salary", "hr")
    util.move_field_to_module(cr, "hr.employee", "driving_license", "l10n_be_hr_contract_salary", "hr")
