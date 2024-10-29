from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "auth_totp_device", "expiration_date", "timestamp without time zone")
    query = """
        UPDATE auth_totp_device
           SET expiration_date = create_date + INTERVAL '90 days'
    """
    util.explode_execute(cr, query, table="auth_totp_device")
