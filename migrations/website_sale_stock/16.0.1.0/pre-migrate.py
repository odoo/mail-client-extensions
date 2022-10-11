# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    renames = [
        eb("website_sale_stock{_wishlist,}.availability_email_body"),
        eb("website_sale_stock{_wishlist,}.ir_cron_send_availability_email"),
    ]
    for rename in renames:
        util.rename_xmlid(cr, *rename)
