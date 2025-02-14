from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "auth_signup.mail_template_user_signup_account_created", util.update_record_from_xml)
