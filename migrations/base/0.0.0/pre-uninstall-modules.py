# -*- coding: utf-8 -*-
import logging
import os

from odoo import modules

from odoo.addons.base.maintenance.migrations import util

_logger = logging.getLogger("odoo.addons.upgrade.base." + __name__)

MODULES_TO_UNINSTALL = util.split_osenv("ODOO_UPG_UNINSTALL_MODULES")


def migrate(cr, version):
    standard_modules = modules.get_modules()
    test_modules = [
        m
        for m in standard_modules
        if m.startswith("test_")
        or m in {"account_test", "l10n_account_edi_ubl_cii_tests", "social_test_full", "theme_test_custo"}
    ]
    for module in test_modules:
        _logger.info("Uninstalling test module %r", module)
        util.uninstall_module(cr, module)

    if not MODULES_TO_UNINSTALL:
        return
    _logger.info(
        "Uninstalling explicitly requested modules: ODOO_UPG_UNINSTALL_MODULES=%s",
        os.environ.get("ODOO_UPG_UNINSTALL_MODULES"),
    )
    for module in MODULES_TO_UNINSTALL:
        cr.execute("SELECT COALESCE(state, 'uninstalled') FROM ir_module_module WHERE name=%s", [module])
        if not cr.rowcount:
            _logger.warning("Module `%s` does not exist, skipping uninstall", module)
        elif cr.fetchone()[0] == "uninstalled":
            _logger.warning("Module `%s` is not installed, skipping uninstall", module)
        elif module in standard_modules or module.startswith("saas_"):
            _logger.warning("Uninstalling `%s` is not supported", module)
        else:
            _logger.info("Uninstalling module %r", module)
            util.uninstall_module(cr, module)
