# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "product.report_simple_label")
    util.remove_view(cr, "product.report_productlabel")
    util.remove_view(cr, "product.report_simple_barcode")
    util.remove_view(cr, "product.report_productbarcode")
    util.remove_record(cr, "product.report_product_label")
    util.remove_record(cr, "product.report_product_product_barcode")
    util.remove_record(cr, "product.report_product_template_barcode")
    util.remove_view(cr, "product.report_producttemplatebarcode")
