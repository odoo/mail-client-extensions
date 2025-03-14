import secrets

import psycopg2.extras

from odoo.upgrade import util


def migrate(cr, version):
    # log when having both phone and mobile, then merge, then remove mobile
    cr.execute(
        """
            INSERT INTO mail_message (author_id, body, date, message_type, model, res_id, subtype_id)
                 SELECT %(root_id)s as author_id,
                        concat('Mobile number ',
                               reg.mobile,
                               ' removed in favor of phone number') as body,
                        now() at time zone 'utc' as date,
                        'notification' as message_type,
                        'event.registration' AS model,
                        reg.id as res_id,
                        %(note_id)s as subtype_id
                   FROM event_registration AS reg
                  WHERE reg.phone IS NOT NULL AND
                        reg.mobile IS NOT NULL AND
                        reg.phone != reg.mobile
        """,
        {"root_id": util.ref(cr, "base.partner_root"), "note_id": util.ref(cr, "mail.mt_note")},
    )
    cr.execute(
        """
            UPDATE event_registration
               SET phone = mobile
             WHERE phone IS NULL and mobile IS NOT NULL
        """
    )
    util.remove_field(cr, "event.registration", "mobile")

    # Remove views that inherited from parent views, since we merged those views together.
    util.remove_field(cr, "res.config.settings", "module_event_barcode")
    util.remove_view(cr, "event.event_report_template_full_page_ticket_inherit_barcode")
    util.remove_view(cr, "event.event_report_template_foldable_badge_inherit_barcode")
    util.remove_view(cr, "event.event_registration_view_form_inherit_barcode")
    util.remove_view(cr, "event.event_event_view_form")

    if not util.column_exists(cr, "event_registration", "barcode"):
        util.create_column(cr, "event_registration", "barcode", "varchar")

        ncr = util.named_cursor(cr, 1000)
        ncr.execute(
            """
            SELECT event_reg.id AS id
              FROM event_registration AS event_reg
              JOIN event_event AS event
                ON event.id = event_reg.event_id
             WHERE event.date_end > NOW()
               AND event.active
                """
        )

        res = ncr.fetchmany(1000)
        dup_query = "SELECT unnest((array_agg(id))[2:]) FROM event_registration WHERE barcode IS NOT NULL GROUP BY barcode HAVING COUNT(*) > 1"
        upd_query = "UPDATE event_registration SET barcode = (%s::jsonb->id::text)::text WHERE id IN %s"
        while res:
            data = {r[0]: secrets.randbits(64) for r in res}
            cr.execute(upd_query, [psycopg2.extras.Json(data), tuple(data)])
            res = ncr.fetchmany(1000)
        ncr.close()

        # Handling duplicates
        cr.execute(dup_query)
        while cr.rowcount:
            data = {r[0]: secrets.randbits(64) for r in cr.fetchall()}

            cr.execute(upd_query, [psycopg2.extras.Json(data), tuple(data)])
            cr.execute(dup_query)

    util.remove_field(cr, "event.event", "auto_confirm")
    util.remove_field(cr, "event.type", "auto_confirm")
    util.remove_field(cr, "event.event", "seats_unconfirmed")
    util.remove_field(cr, "event.type.ticket", "seats_unconfirmed")
    util.rename_field(cr, "event.event", "seats_expected", "seats_taken")
    util.rename_field(cr, "event.type.ticket", "seats_expected", "seats_taken")
