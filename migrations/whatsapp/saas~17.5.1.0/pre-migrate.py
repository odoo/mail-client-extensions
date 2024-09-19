from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        UPDATE whatsapp_template
           SET template_type = 'marketing'
         WHERE template_type is NULL
        """
    )
    util.remove_field(cr, "discuss.channel", "whatsapp_mail_message_id")
