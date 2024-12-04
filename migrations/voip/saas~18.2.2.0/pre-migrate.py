from odoo.upgrade import util


def migrate(cr, version):
    query = """
        WITH info AS (
            SELECT m.id,
                   m.phone,
                   m.mobile
              FROM mail_activity m
             WHERE m.mobile IS NOT NULL
               AND m.phone IS DISTINCT FROM m.mobile
               AND {parallel_filter}
        ), _upd AS (
            UPDATE mail_activity
               SET phone = info.mobile
              FROM info
             WHERE mail_activity.id = info.id
               AND info.phone IS NULL
         RETURNING mail_activity.id
        )
        INSERT INTO mail_message (
                    res_id, model, author_id, message_type,
                    body, date
        )
             SELECT id, 'mail.activity', %s, 'notification',
                    'Previous Mobile: ' || mobile, NOW() at time zone 'UTC'
               FROM info
              WHERE phone IS NOT NULL
    """

    util.explode_execute(
        cr, cr.mogrify(query, [util.ref(cr, "base.partner_root")]).decode(), table="mail_activity", alias="m"
    )

    util.remove_field(cr, "mail.activity", "mobile")
