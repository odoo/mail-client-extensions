# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_field(cr, "account.invoice.line", "layout_category_id")
    util.remove_field(cr, "account.invoice.line", "layout_category_sequence")
    util.remove_field(cr, "sale.order.line", "layout_category_id")
    util.remove_field(cr, "sale.order.line", "layout_category_sequence")
