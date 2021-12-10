# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):

    util.remove_constraint(cr, "calendar_attendee", "calendar_attendee_google_id_uniq")

    # partner is now required on attendees
    Partner = util.env(cr)["res.partner"]
    cr.execute("SELECT max(id) FROM res_partner")
    [max_id] = cr.fetchone()

    cr.execute(
        """
            SELECT email, (array_agg(common_name ORDER BY id desc) FILTER (WHERE common_name IS NOT NULL))[1], array_agg(id)
              FROM calendar_attendee
             WHERE partner_id IS NULL
               AND email IS NOT NULL
          GROUP BY email
             UNION ALL
            SELECT NULL, common_name, array_agg(id)
              FROM calendar_attendee
             WHERE partner_id IS NULL
               AND email IS NULL
          GROUP BY common_name
        """
    )
    for email, name, attendee_ids in cr.fetchall():
        if email:
            partner = Partner.find_or_create(email, assert_valid_email=False)
            if partner.id > max_id:
                partner.name = name or email
            partner_id = partner.id
        else:
            partner_id = Partner.name_create(name or "?")[0]

        cr.execute("UPDATE calendar_attendee SET partner_id = %s WHERE id = ANY(%s)", [partner_id, attendee_ids])

    util.remove_column(cr, "calendar_attendee", "email")  # now a related field

    # events & recurrences
    cr.execute("UPDATE calendar_event SET byday='-1' WHERE recurrency=TRUE AND byday IN ('4', '5')")
    cr.execute(
        """
        UPDATE calendar_event
          SET day = 1
        WHERE recurrency = TRUE
          AND day NOT BETWEEN 1 AND 31
          AND rrule_type = 'monthly'
        """
    )

    # Avoid null values in boolean columns
    # Note: this surprisingly fast.
    cr.execute(
        """
            ALTER TABLE calendar_event
            ALTER COLUMN mo TYPE boolean USING (mo IS TRUE),
            ALTER COLUMN tu TYPE boolean USING (tu IS TRUE),
            ALTER COLUMN we TYPE boolean USING (we IS TRUE),
            ALTER COLUMN th TYPE boolean USING (th IS TRUE),
            ALTER COLUMN fr TYPE boolean USING (fr IS TRUE),
            ALTER COLUMN sa TYPE boolean USING (sa IS TRUE),
            ALTER COLUMN su TYPE boolean USING (su IS TRUE)
        """
    )

    cr.execute(
        """
        UPDATE calendar_event
           SET mo = week_list='MO',
               tu = week_list='TU',
               we = week_list='WE',
               th = week_list='TH',
               fr = week_list='FR',
               sa = week_list='SA',
               su = week_list='SU'
         WHERE rrule_type = 'weekly'
           AND recurrency = TRUE
           AND week_list IS NOT NULL
           AND false = ALL(ARRAY[mo, tu, we, th, fr, sa, su])
    """
    )
    # Sometimes, nothing gives you a day except start date...
    cr.execute(
        """
        UPDATE calendar_event
           SET mo = (date_part('isodow', COALESCE(start_date, start_datetime))=1),
               tu = (date_part('isodow', COALESCE(start_date, start_datetime))=2),
               we = (date_part('isodow', COALESCE(start_date, start_datetime))=3),
               th = (date_part('isodow', COALESCE(start_date, start_datetime))=4),
               fr = (date_part('isodow', COALESCE(start_date, start_datetime))=5),
               sa = (date_part('isodow', COALESCE(start_date, start_datetime))=6),
               su = (date_part('isodow', COALESCE(start_date, start_datetime))=7)
         WHERE rrule_type = 'weekly'
           AND recurrency = TRUE
           AND false = ALL(ARRAY[mo, tu, we, th, fr, sa, su])
    """
    )

    # update null interval as it will lead to infinite loops
    cr.execute(
        """
           UPDATE calendar_event
              SET interval = 1
            WHERE coalesce(interval, 0) <= 0
        RETURNING id, name
        """
    )
    updated_events = [f"<li>{name} (id: {id})</li>" for id, name in cr.fetchall()]

    if updated_events:
        util.add_to_migration_reports(
            category="Events",
            message="""
                 <details>
                    <summary>
                        While upgrading your database, we found that some recurring
                        calendar events had invalid `interval` value (not set, set to 0 or to a negative value).
                        These faulty intervals have been set to their default value which is 1.
                        Please check the updated events to be sure that this default value
                        fits your needs.
                    </summary>
                    <h4>Updated calendar events</h4>
                    <ul>
                    %s
                    </ul>
                </details>
            """
            % (" ".join(updated_events)),
            format="html",
        )

    util.update_field_references(cr, "start_datetime", "start", only_models=("calendar.event",))
    util.update_field_references(cr, "stop_datetime", "stop", only_models=("calendar.event",))

    for field in "start_datetime stop_datetime display_start state is_attendee recurrent_id recurrent_id_date".split():
        util.remove_field(cr, "calendar.event", field)

    util.rename_field(cr, "calendar.event", "final_date", "until")
    util.rename_field(cr, "calendar.event", "week_list", "weekday")
    util.create_column(cr, "calendar_event", "recurrence_id", "int4")
