# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "event_sale.event_registration_report_template_badge")
    util.remove_view(cr, "event_sale.event_event_report_template_badge")
    util.remove_view(cr, "event_sale.event_sale_product_template_form")

    util.parallel_execute(cr, util.explode_query_range(cr, """
        UPDATE product_template
           SET detailed_type = 'event'
         WHERE event_ok = TRUE
    """, table="product_template"))
    util.remove_field(cr, 'product.template', 'event_ok')
