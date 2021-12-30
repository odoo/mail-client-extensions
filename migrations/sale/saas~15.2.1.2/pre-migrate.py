# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "sale.order.line", "qty_delivered_manual")
    util.remove_view(cr, "sale.report_invoice_document_inherit_sale")
    util.remove_model(cr, "report.all.channels.sales")
    util.remove_model(cr, "report.sale.report_saleproforma")

    util.rename_xmlid(cr, "sale_management.menu_product_attribute_action", "sale.menu_product_attribute_action")
