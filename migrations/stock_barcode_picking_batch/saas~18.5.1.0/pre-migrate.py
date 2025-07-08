from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "stock_barcode_picking_batch.view_quant_package_form_inherit_stock_barcode_picking_batch")
