from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "amazon.account", "aws_access_key")
    util.remove_field(cr, "amazon.account", "aws_secret_key")
    util.remove_field(cr, "amazon.account", "aws_session_token")
    util.remove_field(cr, "amazon.account", "aws_credentials_expiry")
