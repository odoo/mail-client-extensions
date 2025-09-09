# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # working on one record at a time seems faster... Maybe it should not work in chunks...
    # If slow, see below for a way to bootstrap these fields using a specific upgrade script
    # https://github.com/odoo/migration-scripts/commit/f4caab2e581d87d03a6f3d0399686dc4a411ad2b#diff-358428b7812a500c0a8a1f4be1978074
    query = "SELECT id FROM sale_order WHERE delivery_price IS NULL"
    util.recompute_fields(cr, "sale.order", ["delivery_price"], chunk_size=1, query=query)
