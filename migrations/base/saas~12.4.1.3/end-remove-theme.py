# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    for theme in "artists beauty bookstore odoo_experts orchid real_estate vehicle yes".split():
        util.remove_theme(cr, f"theme_{theme}_sale", f"theme_{theme}")
