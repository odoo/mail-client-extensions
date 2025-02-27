from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "sign.mail_activity_type_form_inherit")
