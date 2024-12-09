from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "mail.mail_template_view_form_confirm_delete")
    util.remove_field(cr, "res.company", "alias_domain_name")

    cr.execute("DROP INDEX IF EXISTS unique_mail_message_id_res_partner_id_if_set")
    cr.execute("ALTER TABLE discuss_channel DROP CONSTRAINT IF EXISTS discuss_channel_sub_channel_no_group_public_id")
    util.explode_execute(
        cr,
        """
        UPDATE discuss_channel
           SET group_public_id = parent.group_public_id
          FROM discuss_channel parent
         WHERE discuss_channel.parent_channel_id = parent.id
    """,
        table="discuss_channel",
    )
    if util.module_installed(cr, "website_slides"):
        util.move_field_to_module(cr, "mail.activity", "request_partner_id", "mail", "website_slides")
    else:
        util.remove_field(cr, "mail.activity", "request_partner_id")
