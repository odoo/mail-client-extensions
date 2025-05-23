from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "stock.move", "description_bom_line")
    util.remove_field(cr, "stock.move.line", "description_bom_line")
    util.remove_view(cr, "mrp.view_stock_move_line_detailed_operation_tree_mrp")
