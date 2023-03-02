# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "sale.order.line", "event_ok")
    util.create_column(cr, "event_event_ticket", "price_incl", "int4")
