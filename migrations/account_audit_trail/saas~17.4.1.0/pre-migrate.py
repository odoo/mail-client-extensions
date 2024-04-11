from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "mail.message", "show_audit_log", "account_audit_log_activated")
