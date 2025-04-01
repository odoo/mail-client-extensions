from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "mail_bot.res_users_view_form_preferences")
