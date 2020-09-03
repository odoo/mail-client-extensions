# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "pos.config", "iface_customer_facing_display", "iface_customer_facing_display_via_proxy")
    util.remove_field(cr, "pos.config", "customer_facing_display_html")
    util.remove_view(cr, "point_of_sale.customer_facing_display_html")
