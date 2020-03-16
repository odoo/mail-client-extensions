# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "sale.order", "remaining_validity_days")
    util.move_field_to_module(cr, "sale_order", "tag_ids", "sale_crm", "sale")
