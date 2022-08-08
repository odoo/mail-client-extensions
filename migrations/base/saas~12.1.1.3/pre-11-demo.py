# -*- coding: utf-8 -*-
import odoo

from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if not util.module_installed(cr, "hr_holidays"):
        return
    cr.execute("SELECT demo FROM ir_module_module WHERE name='hr_holidays'")
    if cr.fetchone()[0]:
        # mark the module in init mode to allow the execution of <function> tags in demo XML files
        odoo.tools.config["init"]["hr_holidays"] = 1
