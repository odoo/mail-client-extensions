# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "pos_order_line", "note", "varchar")
    util.create_column(cr, "pos_order_line", "mp_skip", "boolean")

    util.create_column(cr, "restaurant_printer", "printer_type", "varchar")
