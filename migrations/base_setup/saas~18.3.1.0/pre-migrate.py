from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "res.config.settings", "user_default_rights")
    cr.execute("DELETE FROM ir_config_parameter WHERE key='base_setup.default_user_rights'")
