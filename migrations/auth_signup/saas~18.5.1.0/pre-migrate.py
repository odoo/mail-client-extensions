from odoo.upgrade import util


def migrate(cr, version):
    if util.module_installed(cr, "portal"):
        util.rename_xmlid(cr, "portal.mail_template_data_portal_welcome", "auth_signup.portal_set_password_email")
