from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "account_followup.manual_reminder", "email_add_signature")
