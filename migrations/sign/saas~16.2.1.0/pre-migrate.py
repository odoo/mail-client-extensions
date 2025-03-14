from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "sign_request_item", "ignored", "boolean")
