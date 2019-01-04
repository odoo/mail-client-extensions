# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    cr.execute("SELECT name FROM ir_module_module WHERE state = 'to upgrade' AND name LIKE 'theme\_%'")
    for theme, in cr.fetchall():
        util.uninstall_module(cr, theme)
        util.force_install_module(cr, theme)
