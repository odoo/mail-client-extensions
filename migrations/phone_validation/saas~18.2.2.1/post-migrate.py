from odoo.upgrade import util


def migrate(cr, version):
    if not util.module_installed(cr, "sms"):
        # compute the `phone_sanitized` field.
        util.import_script("sms/saas~12.5.2.0/post-migrate.py").migrate(cr, None)
