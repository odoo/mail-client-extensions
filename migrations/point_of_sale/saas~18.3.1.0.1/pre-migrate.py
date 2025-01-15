from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "res.config.settings", "module_pos_viva_wallet", "module_pos_viva_com")
