from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "stock.picking", "show_mark_as_todo")
    util.remove_model(cr, "stock.quant.reserve")
    util.remove_model(cr, "stock.quant.reserve.line")
