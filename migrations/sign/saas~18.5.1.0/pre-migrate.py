from odoo.upgrade import util


def migrate(cr, version):
    util.remove_column(cr, "sign_send_request", "signers_count")
