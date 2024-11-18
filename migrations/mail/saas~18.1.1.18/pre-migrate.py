from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "mail.mail_template_view_form_confirm_delete")
    util.remove_field(cr, "res.company", "alias_domain_name")

    cr.execute("DROP INDEX IF EXISTS unique_mail_message_id_res_partner_id_if_set")
