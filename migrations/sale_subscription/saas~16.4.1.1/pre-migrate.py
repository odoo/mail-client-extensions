# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.change_field_selection_values(cr, "sale.order.alert", "state", {"done": "sale"})
