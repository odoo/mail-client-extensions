# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    for field in "onss_expeditor_number onss_pem_certificate onss_pem_passphrase".split():
        util.move_field_to_module(cr, "res.company", field, "l10n_be_hr_payroll_dimona", "l10n_be_hr_payroll")
        util.move_field_to_module(cr, "res.config.settings", field, "l10n_be_hr_payroll_dimona", "l10n_be_hr_payroll")
