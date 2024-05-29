from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(
        cr,
        "stock_barcode_barcodelookup.product_product_view_form_stock_barcode_barcodelookup",
    )
