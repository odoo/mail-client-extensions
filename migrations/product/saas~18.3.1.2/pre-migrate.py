from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "uom.uom", "packaging_barcodes_count")
