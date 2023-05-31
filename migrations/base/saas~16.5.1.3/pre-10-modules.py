# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.merge_module(cr, "l10n_ke_hr_payroll_bik", "l10n_ke_hr_payroll")
