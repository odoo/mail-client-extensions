# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    # Remove theme dependencies
    deps = [
        ("artists", "monglia"),
        ("beauty", "loftspace"),
        ("bistro", "treehouse"),
        ("bookstore", "loftspace"),
        ("orchid", "loftspace"),
        ("odoo_experts", "loftspace"),
        ("real_estate", "monglia"),
        ("vehicle", "monglia"),
        ("yes", "kea"),
        ("zap", "treehouse"),
    ]
    for search, unload in deps:
        theme_to_search = util.env(cr).ref(f"base.module_theme_{search}", raise_if_not_found=False)
        theme_to_unload = util.env(cr).ref(f"base.module_theme_{unload}", raise_if_not_found=False)
        if theme_to_search and theme_to_unload:
            websites = util.env(cr)["website"].search([("theme_id", "=", theme_to_search.id)])
            for website in websites:
                theme_to_unload._theme_unload(website)
