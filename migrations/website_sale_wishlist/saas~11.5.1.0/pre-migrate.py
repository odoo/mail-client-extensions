# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute("DELETE FROM product_wishlist WHERE partner_id IS NULL")
    util.remove_field(cr, "product.wishlist", "session", cascade=True)
    util.remove_field(cr, "product.wishlist", "price_new")
    util.remove_field(cr, "res.users", "current_session")
    util.remove_record(cr, 'website_sale_wishlist.product_wishlist_rule')
