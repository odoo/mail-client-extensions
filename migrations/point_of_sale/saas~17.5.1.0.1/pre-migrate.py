from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "pos.config", "module_pos_mercury")
    util.remove_field(cr, "res.config.settings", "module_pos_mercury")
