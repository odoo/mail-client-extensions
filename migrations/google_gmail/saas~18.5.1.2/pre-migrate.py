from odoo.upgrade import util


def migrate(cr, version):
    cr.execute("UPDATE fetchmail_server SET is_ssl = TRUE WHERE server_type = 'gmail' AND is_ssl IS NOT TRUE")
    util.remove_field(cr, "google.gmail.mixin", "google_gmail_authorization_code")
