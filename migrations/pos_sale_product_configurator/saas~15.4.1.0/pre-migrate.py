# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "pos_sale_product_configurator.pos_config_view_form")
    util.remove_field(cr, "pos.config", "iface_open_product_info")
