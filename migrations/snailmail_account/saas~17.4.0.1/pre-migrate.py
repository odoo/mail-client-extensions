from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "account.move.send", "send_by_post_warning_message")
