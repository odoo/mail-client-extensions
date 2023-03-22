# -*- coding: utf-8 -*-
import logging

from odoo import modules

from odoo.addons.base.maintenance.migrations import util

_logger = logging.getLogger("odoo.addons.base.maintenance.migrations.base." + __name__)


def migrate(cr, version):
    test_modules = [
        m
        for m in modules.get_modules()
        if m.startswith("test_")
        or m in {"account_test", "l10n_account_edi_ubl_cii_tests", "social_test_full", "theme_test_custo"}
    ]
    for module in test_modules:
        _logger.info("Uninstalling test module %r", module)
        util.uninstall_module(cr, module)
