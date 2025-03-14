from odoo.upgrade import util


def migrate(cr, version):
    query = """
                UPDATE account_move move
                   SET incoterm_location = po.incoterm_location
                  FROM purchase_order po
                  JOIN purchase_order_line pol ON pol.order_id = po.id
                  JOIN account_move_line aml ON aml.purchase_line_id = pol.id
                 WHERE move.id = aml.move_id
                   AND po.incoterm_location IS NOT NULL
            """
    util.explode_execute(cr, query, table="account_move", alias="move")
