from odoo.upgrade import util


def migrate(cr, version):
    util.rename_xmlid(cr, "mail_bot_hr.res_users_view_form_profile", "mail_bot_hr.res_users_view_form_preferences")
