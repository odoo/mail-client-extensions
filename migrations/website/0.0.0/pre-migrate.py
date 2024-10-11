from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # Index removed on https://github.com/odoo/odoo/pull/37901 (13.0)
    if util.version_between("13.0", "18.0"):
        cr.execute("DROP INDEX IF EXISTS res_users_login_key_unique_website_index")
