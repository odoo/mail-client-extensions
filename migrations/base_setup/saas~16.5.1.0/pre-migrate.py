from odoo.upgrade import util


def migrate(cr, version):
    if util.module_installed(cr, "mail"):
        util.move_field_to_module(cr, "res.config.settings", "external_email_server_default", "base_setup", "mail")
    else:
        util.remove_field(cr, "res.config.settings", "external_email_server_default")
