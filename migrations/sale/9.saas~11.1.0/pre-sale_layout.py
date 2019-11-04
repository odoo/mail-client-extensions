# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.rename_model(cr, "sale_layout.category", "sale.layout_category", rename_table=False)
    for model in {"sale.order.line", "account.invoice.line"}:
        util.rename_field(cr, model, "sale_layout_cat_id", "layout_category_id")
        util.rename_field(cr, model, "categ_sequence", "layout_category_sequence")

    # remove `sale_layout` old inherited views (that will fail)
    util.remove_view(cr, "sale.view_order_form_inherit_1")
    util.remove_view(cr, "sale.view_invoice_form_inherit_1")
    util.remove_view(cr, "sale.view_invoice_line_form_inherit_2")
