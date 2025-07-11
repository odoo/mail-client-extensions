from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "res.config.settings", "allow_out_of_stock_order", "default_allow_out_of_stock_order")
    util.rename_field(cr, "res.config.settings", "available_threshold", "default_available_threshold")
    util.rename_field(cr, "res.config.settings", "show_availability", "default_show_availability")
