from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "stock_barcode.stock_picking_action_form")
