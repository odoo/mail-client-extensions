# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "pos_self_order.first_letter_of_odoo_logo_svg")
    util.remove_view(cr, "pos_self_order.qr_code")
    util.rename_xmlid(cr, "pos_self_order.index", "pos_self_order.mobile_index")
