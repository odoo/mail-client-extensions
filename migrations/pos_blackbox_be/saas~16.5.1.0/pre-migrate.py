# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_model(cr, "pos.order_line_pro_forma_be")
    util.remove_model(cr, "pos.order_pro_forma_be")
    util.remove_view(cr, "pos_blackbox_be.view_pos_blackbox_be_pro_forma_tree")
    util.remove_view(cr, "pos_blackbox_be.pos_config_view_form_inherit_blackbox_be")
    util.remove_field(cr, "pos.order", "receipt_type")
    util.remove_field(cr, "pos.session", "pro_forma_order_ids")
