# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "sale.order.line", "qty_delivered_manual")
    util.remove_view(cr, "sale.report_invoice_document_inherit_sale")
    util.remove_model(cr, "report.all.channels.sales")
    util.remove_model(cr, "report.sale.report_saleproforma")

    util.rename_xmlid(cr, "sale_management.menu_product_attribute_action", "sale.menu_product_attribute_action")

    util.remove_record(cr, "sale.action_sale_order_form_view")
    util.remove_view(cr, "sale.product_template_sale_form_view")
    util.remove_view(cr, "sale.product_template_form_view_invoice_policy")

    util.remove_view(cr, "sale.mail_notification_paynow_online")
