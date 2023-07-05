# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "sale.order.log.report", "recurring_yearly_graph")
    util.remove_field(cr, "sale.order.log.report", "recurring_monthly_graph")
    util.remove_field(cr, "sale.order.log.report", "amount_signed_graph")
