# -*- coding: utf-8 -*-
from operator import itemgetter
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    env = util.env(cr)
    cr.execute("SELECT id FROM pos_order_line")
    ids = list(map(itemgetter(0), cr.fetchall()))
    orderlines = util.iter_browse(env["pos.order.line"], ids)
    for orderline in orderlines:
        orderline._onchange_amount_line_all()

    cr.execute("SELECT id FROM pos_order")
    ids = list(map(itemgetter(0), cr.fetchall()))
    orders = util.iter_browse(env["pos.order"], ids)
    for order in orders:
        order._onchange_amount_all()
