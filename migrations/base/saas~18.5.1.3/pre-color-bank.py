from odoo.upgrade import util


def migrate(cr, version):
    if util.module_installed(cr, "account"):
        util.move_field_to_module(cr, "res.partner.bank", "color", "account", "base")
