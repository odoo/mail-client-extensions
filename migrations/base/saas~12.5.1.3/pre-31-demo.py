# -*- coding: utf-8 -*-
import odoo
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.module_installed(cr, "test_l10n_be_hr_payroll_account"):
        # Force module in init mode to call <function> tags
        # Avoid warning on CI
        odoo.tools.config["init"]["test_l10n_be_hr_payroll_account"] = "1"
