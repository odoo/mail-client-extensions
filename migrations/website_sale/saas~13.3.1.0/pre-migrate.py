# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "website_sale.product_supplierinfo_public")
    util.remove_record(cr, "website_sale.access_product_supplierinfo")
    util.remove_record(cr, "website_sale.access_product_supplierinfo_user")
