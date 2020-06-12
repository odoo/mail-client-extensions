# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_theme(cr, "theme_artists_sale", "theme_artists")
    util.remove_theme(cr, "theme_real_estate_sale", "theme_real_estate")
    util.remove_theme(cr, "theme_odoo_experts_sale", "theme_odoo_experts")

