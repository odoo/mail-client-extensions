# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("{test_l10n_be_hr_payroll_account,l10n_be_hr_payroll}.work_entry_type_phc"))
