# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, 'website_sale.product_supplierinfo_public')
