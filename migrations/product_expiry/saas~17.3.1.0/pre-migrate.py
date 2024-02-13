from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "product_expiry.report_package_barcode_expiry")
