# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.force_noupdate(cr, 'website.menu_website', False)                  # force removal
    util.force_noupdate(cr, 'website.menu_website_configuration', False)    # force rename
