from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "account.move.send", "send_mail_warning_message")
    util.remove_field(cr, "account.move.send", "sequence_gap_warning")
