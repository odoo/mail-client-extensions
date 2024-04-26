from odoo.upgrade import util


def migrate(cr, version):
    util.remove_column(cr, "res_config_settings", "pos_iface_orderline_notes")
