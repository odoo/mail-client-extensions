from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "point_of_sale.pos_iot_config_view_form")
    util.make_field_non_stored(cr, "res.config.settings", "pos_epson_printer_ip", selectable=True)
