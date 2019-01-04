# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):

    cr.execute("SELECT name FROM ir_module_module WHERE name like 'theme\_%' AND name != 'theme_common' AND state='installed'")

    for installed_theme in [s[0] for s in cr.fetchall()]:
        vkey=installed_theme+'.compatibility-saas-11-4%'
        cr.execute("UPDATE theme_ir_ui_view SET active=TRUE WHERE key LIKE %s", (vkey,));
        cr.execute("UPDATE ir_ui_view SET active=TRUE WHERE key LIKE %s", (vkey,));


