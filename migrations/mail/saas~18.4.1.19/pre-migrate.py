from odoo.upgrade import util


def migrate(cr, version):
    util.remove_model(cr, "mail.resend.message")
    util.remove_model(cr, "mail.resend.partner")

    util.remove_field(cr, "mail.compose.message", "notified_bcc")
    util.remove_field(cr, "mail.compose.message", "show_notified_bcc")
    util.remove_field(cr, "mail.scheduled.message", "notified_bcc")
    util.remove_field(cr, "mail.scheduled.message", "show_notified_bcc")
