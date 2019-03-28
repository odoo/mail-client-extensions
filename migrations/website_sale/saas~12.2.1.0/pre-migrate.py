# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_field(cr, "product.public.category", *eb("product{,_template}_image_ids"))
    util.rename_field(cr, "product.image", "image", "image_raw_original")
    util.create_column(cr, "product_image", "can_image_raw_be_zoomed", "boolean")

    cr.execute("UPDATE rating_rating SET rating = rating * 2 WHERE res_model = 'product.template'")

    util.remove_view(cr, "website_sale.product_template_form_view")
