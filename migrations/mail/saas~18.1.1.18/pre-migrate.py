from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "mail.mail_template_view_form_confirm_delete")
