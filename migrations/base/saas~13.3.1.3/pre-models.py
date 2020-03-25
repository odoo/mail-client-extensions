# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    if util.column_exists(cr, "res_partner", "barcode"):
        util.convert_field_to_property(cr, "res.partner", "barcode", "char")
