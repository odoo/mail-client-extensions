from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "mail.ir_cron_send_scheduled_message", util.update_record_from_xml)

    util.create_column(cr, "mail_activity", "user_tz", "varchar")
    util.explode_execute(
        cr,
        """
        UPDATE mail_activity activity
           SET user_tz = partner.tz
          FROM res_users users
          JOIN res_partner partner
            ON partner.id = users.partner_id
         WHERE users.id = activity.user_id
           AND partner.tz IS DISTINCT FROM activity.user_tz
        """,
        table="mail_activity",
        alias="activity",
    )
