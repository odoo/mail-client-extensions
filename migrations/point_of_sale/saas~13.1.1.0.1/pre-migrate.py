# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    # pos.config
    util.remove_field(cr, "pos.config", "use_existing_lots")
    util.create_column(cr, "pos_config", "rounding_method", "int4")
    util.create_column(cr, "pos_config", "cash_rounding", "boolean")
    util.create_column(cr, "pos_config", "only_round_cash_method", "boolean")

    # pos.session
    util.create_column(cr, "pos_session", "cash_real_difference", "numeric")
    util.create_column(cr, "pos_session", "cash_real_transaction", "numeric")
    util.create_column(cr, "pos_session", "cash_real_expected", "numeric")
    util.create_column(cr, "pos_session", "update_stock_at_closing", "boolean")

    cr.execute("UPDATE pos_session SET update_stock_at_closing = true")

    # res.company
    util.create_column(cr, "res_company", "point_of_sale_update_stock_quantities", "varchar")
    cr.execute("UPDATE res_company SET point_of_sale_update_stock_quantities = 'closing'")

    # stock.picking
    util.create_column(cr, "stock_picking", "pos_session_id", "int4")
    util.create_column(cr, "stock_picking", "pos_order_id", "int4")
    cr.execute(
        """
        UPDATE stock_picking p
           SET pos_session_id = o.session_id,
               pos_order_id = o.id
          FROM pos_order o
         WHERE p.id = o.picking_id

    """
    )

    # pos.order
    util.remove_field(cr, "pos.order", "picking_id")
    util.remove_field(cr, "pos.order", "location_id")

    # pos.order.report
    util.remove_field(cr, "report.pos.order", "location_id")

    # remove views stolen from `pos_cash_rounding`
    gone_views = """
        pos_order_view_form_inherit_cash_rounding
        pos_config_view_form_inherit_cash_rounding
        res_config_view_form_inherit_pos_cash_rounding
    """
    for view in util.splitlines(gone_views):
        util.remove_view(cr, f"point_of_sale.{view}")
