# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.change_field_selection_values(cr, "barcode.rule", "type", {"qty_done": "quantity"})
