# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_field(cr, "pos.config", "barcode_scanner")
    util.remove_field(cr, "res.users", "pos_security_pin")
    util.remove_view(cr, 'point_of_sale.res_users_view_form')
    util.remove_view(cr, 'point_of_sale.pos_config_view_form')
