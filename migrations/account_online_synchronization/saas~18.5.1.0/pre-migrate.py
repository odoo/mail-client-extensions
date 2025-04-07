from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "account.online.link", "provider_data")
