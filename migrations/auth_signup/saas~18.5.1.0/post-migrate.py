from odoo.upgrade import util


def migrate(cr, version):
    if util.module_installed(cr, "portal"):
        util.if_unchanged(cr, "auth_signup.portal_set_password_email", util.update_record_from_xml)
        cr.execute(
            """
            UPDATE mail_template
               SET template_fs = 'auth_signup/data/mail_template_data.xml'
             WHERE id = %s
               AND template_fs = 'portal/data/mail_template_data.xml'
            """,
            [util.ref(cr, "auth_signup.portal_set_password_email")],
        )
