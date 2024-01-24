# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.update_record_from_xml(cr, "website_sale.product_pricelist_comp_rule")
    util.update_record_from_xml(cr, "website_sale.product_pricelist_item_comp_rule")
