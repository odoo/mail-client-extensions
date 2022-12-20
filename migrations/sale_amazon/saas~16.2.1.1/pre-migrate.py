# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "crm.team", "amazon_team")
    util.remove_field(cr, "stock.location", "amazon_location")

    util.create_column(cr, "stock_picking", "amazon_sync_status", "varchar")
    query = """
        UPDATE stock_picking
           SET amazon_sync_status = 'pending'
         WHERE amazon_sync_pending = TRUE
    """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="stock_picking"))
    util.remove_field(cr, "stock.picking", "amazon_sync_pending")
