from odoo.upgrade import util


def migrate(cr, version):
    # Convert the old Many2one analytic_account_line_id fields to Many2many fields for WO (x2) and stock.move
    util.create_m2m(cr, "account_analytic_line_stock_move_rel", "stock_move", "account_analytic_line")
    query = """
        INSERT INTO account_analytic_line_stock_move_rel (stock_move_id, account_analytic_line_id)
        SELECT id, analytic_account_line_id FROM stock_move WHERE analytic_account_line_id IS NOT NULL
    """
    cr.execute(query)
    util.remove_field(cr, "stock.move", "analytic_account_line_id")
