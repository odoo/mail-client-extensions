# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    view_list = [
        "view_purchase_config",
        "purchase_order_2_stock_picking",
        "view_product_normal_purchase_buttons_from",
        "purchase_order_line_form",
        "view_purchase_line_invoice",
        "view_request_for_quotation_filter",
        "view_purchase_order_group",
    ]
    for view in view_list:
        util.remove_view(cr, "purchase." + view)

    for r in "order quotation".split():
        util.force_noupdate(cr, "purchase.report_purchase%s" % r, False)
        util.force_noupdate(cr, "purchase.report_purchase%s_document" % r, False)
