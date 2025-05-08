from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "repair.order", "is_returned")
    util.remove_field(cr, "stock.picking", "is_repairable")
    util.remove_field(cr, "stock.picking.type", "is_repairable")
    util.remove_field(cr, "stock.picking.type", "return_type_of_ids")
