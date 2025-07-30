from odoo.upgrade import util


def migrate(cr, version):
    query = """
        UPDATE stock_picking p
           SET ticket_id = rel.helpdesk_ticket_id
          FROM helpdesk_ticket_stock_picking_rel rel
         WHERE p.id = rel.stock_picking_id
    """
    util.explode_execute(cr, query, table="stock_picking", alias="p")
