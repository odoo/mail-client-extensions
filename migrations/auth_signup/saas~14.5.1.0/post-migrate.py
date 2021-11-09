# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(
        cr, "auth_signup.reset_password_email", util.update_record_from_xml, reset_translations={"body_html"}
    )
    util.if_unchanged(
        cr, "auth_signup.set_password_email", util.update_record_from_xml, reset_translations={"subject", "body_html"}
    )
    util.if_unchanged(
        cr,
        "auth_signup.mail_template_data_unregistered_users",
        util.update_record_from_xml,
        reset_translations={"body_html"},
    )
    util.if_unchanged(
        cr,
        "auth_signup.mail_template_user_signup_account_created",
        util.update_record_from_xml,
        reset_translations={"subject", "body_html"},
    )
