# -*- coding: utf-8 -*-

from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.force_noupdate(cr, "website_forum.menu_questions", False)
