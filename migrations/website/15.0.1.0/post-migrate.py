# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # Replay those theme bridge module removal scripts, as some DBs got migrated
    # without the original script (created after release), see commit message.
    util.remove_theme(cr, "theme_avantgarde_blog", "theme_avantgarde")

    util.remove_theme(cr, "theme_artists_sale", "theme_artists")
    util.remove_theme(cr, "theme_beauty_sale", "theme_beauty")
    util.remove_theme(cr, "theme_bookstore_sale", "theme_bookstore")
    util.remove_theme(cr, "theme_odoo_experts_sale", "theme_odoo_experts")
    util.remove_theme(cr, "theme_orchid_sale", "theme_orchid")
    util.remove_theme(cr, "theme_real_estate_sale", "theme_real_estate")
    util.remove_theme(cr, "theme_vehicle_sale", "theme_vehicle")
    util.remove_theme(cr, "theme_yes_sale", "theme_yes")

    util.remove_theme(cr, "theme_graphene_blog", "theme_graphene")

    util.remove_theme(cr, "theme_anelusia_sale", "theme_anelusia")
    util.remove_theme(cr, "theme_kea_sale", "theme_kea")
    util.remove_theme(cr, "theme_kiddo_sale", "theme_kiddo")
    util.remove_theme(cr, "theme_loftspace_sale", "theme_loftspace")
    util.remove_theme(cr, "theme_monglia_sale", "theme_monglia")
    util.remove_theme(cr, "theme_notes_sale", "theme_notes")
