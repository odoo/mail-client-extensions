from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "google_account.config_google_redirect_uri")
