# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    if util.has_enterprise():
        util.merge_module(cr, "l10n_be_hr_payroll_eco_vouchers", "l10n_be_hr_payroll")
