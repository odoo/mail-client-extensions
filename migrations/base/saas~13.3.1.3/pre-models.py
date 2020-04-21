# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.move_field_to_module(cr, "res.partner", "barcode", "point_of_sale", "base")
    if util.column_exists(cr, "res_partner", "barcode"):
        util.convert_field_to_property(cr, "res.partner", "barcode", "char")

    util.remove_field(cr, "res.partner.bank", "qr_code_valid")
    util.remove_field(cr, "account.setup.bank.manual.config", "qr_code_valid")
