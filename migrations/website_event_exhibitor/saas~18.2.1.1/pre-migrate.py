from odoo.upgrade import util


def migrate(cr, version):
    query = """
        WITH info AS (
            SELECT s.id,
                   s.phone,
                   s.mobile
              FROM event_sponsor s
             WHERE s.mobile IS NOT NULL
               AND s.phone IS DISTINCT FROM s.mobile
               AND {parallel_filter}
        ), _upd AS (
            UPDATE event_sponsor
               SET phone = info.mobile
              FROM info
             WHERE event_sponsor.id = info.id
               AND info.phone IS NULL
         RETURNING event_sponsor.id
        )
        INSERT INTO mail_message (
                    res_id, model, author_id, message_type,
                    body, date
        )
             SELECT id, 'event.sponsor', %s, 'notification',
                    'Previous Mobile: ' || mobile, NOW() at time zone 'UTC'
               FROM info
              WHERE phone IS NOT NULL
    """

    util.explode_execute(
        cr, cr.mogrify(query, [util.ref(cr, "base.partner_root")]).decode(), table="event_sponsor", alias="s"
    )

    util.remove_field(cr, "event.sponsor", "mobile")
    util.remove_field(cr, "event.sponsor", "partner_mobile")
