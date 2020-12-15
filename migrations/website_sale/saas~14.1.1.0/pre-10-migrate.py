# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    # The Terms and Conditions are converted to an HTML field and saved on the company.
    WR = util.env(cr)["website.rewrite"]
    WR.create({"name": "Terms & Conditions", "url_from": "/shop/terms", "url_to": "/terms", "redirect_type": "301"})
    util.remove_view(cr, "website_sale.terms")

    cr.execute(
        "UPDATE website_snippet_filter SET website_id = NULL WHERE id = %s",
        [util.ref(cr, "website.dynamic_filter_demo_products")],
    )
