from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "discuss_channel", "allow_public_upload", "bool", default=False)
