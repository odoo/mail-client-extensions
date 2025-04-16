from odoo.upgrade import util


def migrate(cr, version):
    util.remove_model(cr, "mail.resend.message")
    util.remove_model(cr, "mail.resend.partner")
