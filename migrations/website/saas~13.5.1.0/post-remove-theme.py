# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_theme(cr, "theme_graphene_blog", "theme_graphene")

    util.remove_theme(cr, "theme_anelusia_sale", "theme_anelusia")
    util.remove_theme(cr, "theme_kea_sale", "theme_kea")
    util.remove_theme(cr, "theme_kiddo_sale", "theme_kiddo")
    util.remove_theme(cr, "theme_loftspace_sale", "theme_loftspace")
    util.remove_theme(cr, "theme_monglia_sale", "theme_monglia")
    util.remove_theme(cr, "theme_notes_sale", "theme_notes")
