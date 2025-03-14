from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "base.change_password_user_form_view")
    util.remove_record(cr, "base.change_password_action_server")
