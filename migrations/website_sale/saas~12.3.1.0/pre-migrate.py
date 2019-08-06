# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("website_sale.{website_sale,snippet_options}"))
    util.remove_view(cr, 'website_sale.account_invoice_view_form')

    for model in ('product.template', 'product.product'):
        for field in ('website_price', 'website_public_price', 'website_price_difference'):
            util.remove_field(cr, model, field)
