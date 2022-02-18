# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "pos_order_line", "uuid", "varchar")
    util.remove_field(cr, "pos.order.line", "mp_dirty")
    query = """
        UPDATE pos_order
        SET multiprint_resume = NULL
        WHERE state = 'draft'
    """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="pos_order"))
    util.remove_view(cr, "pos_restaurant.pos_config_view_form_inherit_restaurant")
