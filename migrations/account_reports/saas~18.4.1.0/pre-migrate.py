from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "account.return", "attachment_count")
