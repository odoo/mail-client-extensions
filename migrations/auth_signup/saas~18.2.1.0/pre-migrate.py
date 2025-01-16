from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "auth_signup.alert_login_new_device")
