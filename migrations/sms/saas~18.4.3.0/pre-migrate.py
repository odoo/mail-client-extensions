from odoo.upgrade import util


def migrate(cr, version):
    util.remove_model(cr, "sms.resend")
    util.remove_model(cr, "sms.resend.recipient")
