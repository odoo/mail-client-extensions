from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("auth_totp_mail.account_security_{setting_update,alert}"))
