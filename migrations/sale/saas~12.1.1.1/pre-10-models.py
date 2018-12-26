# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_field(cr, "product.pricelist", "discount_policy")
    util.remove_field(cr, "product.template", "hide_expense_policy")
    util.remove_field(cr, "crm.team", "use_quotations")
    util.remove_field(cr, "crm.team", "use_invoices")
    util.remove_field(cr, "crm.team", "dashboard_graph_model")

    util.remove_view(cr, "sale.report_all_channels_sales_view_pivot")
    util.remove_view(cr, "sale.report_all_channels_sales_view_search")
    util.remove_view(cr, "sale.product_template_form_view_invoice_policy")
