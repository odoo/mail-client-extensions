from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "res.config.settings", "group_barcode_show_quantity_count")
    util.remove_field(cr, "res.config.settings", "group_barcode_count_entire_location")
    util.remove_record(cr, "stock_barcode.group_barcode_show_quantity_count")
    util.remove_record(cr, "stock_barcode.group_barcode_count_entire_location")
