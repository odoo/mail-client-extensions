# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):

    util.remove_field(cr, 'res.partner', 'speaker')
    util.remove_view(cr, 'event.view_event_partner_info_form')

    util.create_column(cr, 'event_event', 'seats_availability', 'varchar')
    cr.execute("""UPDATE event_event
                     SET seats_availability=CASE WHEN coalesce(seats_max, 0) = 0
                                                 THEN 'unlimited'
                                                 ELSE 'limited'
                                            END
               """)

    # create and fill new models
    cr.execute("""CREATE TABLE event_mail(
                    id SERIAL PRIMARY KEY,
                    event_id integer,
                    interval_nbr integer,
                    interval_unit varchar,
                    interval_type varchar,
                    template_id integer,
                    scheduled_date timestamp without time zone,
                    mail_sent boolean,
                    done boolean
                  )
               """)
    cr.execute("""CREATE TABLE event_mail_registration(
                    id SERIAL PRIMARY KEY,
                    scheduler_id integer,
                    registration_id integer,
                    scheduled_date timestamp without time zone,
                    mail_sent boolean
                  )
               """)

    cr.execute("""INSERT INTO event_mail(event_id, interval_nbr, interval_unit, interval_type,
                                         template_id, scheduled_date, mail_sent, done)
                  SELECT id, 0, 'now', 'after_sub', email_registration_id,
                         CASE WHEN state in ('confirm', 'done') THEN create_date
                         ELSE NULL END,
                         true,
                         CASE WHEN state = 'done' THEN true
                         ELSE NOT EXISTS(SELECT 1 FROM event_registration WHERE event_id = e.id
                                         AND state = 'draft')
                         END
                   FROM event_event e
                  WHERE email_registration_id IS NOT NULL
               """)
    cr.execute("""INSERT INTO event_mail_registration(scheduler_id, registration_id,
                                                      scheduled_date, mail_sent)
                  SELECT s.id, r.id, r.date_open, r.state != 'draft'
                    FROM event_registration r
                    JOIN event_mail s
                      ON s.event_id = r.event_id
               """)
