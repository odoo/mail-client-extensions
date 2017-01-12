# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # applicants have light activities
    # only date & message

    cr.execute("""
        INSERT INTO mail_message(
            model, res_id, record_name, author_id, date, message_type, body, subtype_id
        )
             SELECT 'hr.applicant', a.id, a.name, u.partner_id,
                    COALESCE(a.date_action, a.write_date, a.create_date),
                    'comment', a.title_action, %s
               FROM hr_applicant a
               JOIN res_users u ON (u.id = COALESCE(a.write_uid, a.create_uid, 1))
              WHERE a.title_action IS NOT NULL
                AND COALESCE(a.date_action, to_timestamp(0)) < now() at time zone 'utc'
    """, [util.ref(cr, 'mail.mt_activities')])

    cr.execute("""
        INSERT INTO mail_activity(activity_type_id, user_id,
                                  res_model_id, res_id, res_model, res_name,
                                  summary, date_deadline)
             SELECT %s, COALESCE(write_uid, create_uid, 1),
                    (SELECT id FROM ir_model WHERE model='hr.applicant'), id, 'hr.applicant', name,
                    title_action, date_action
               FROM hr_applicant
              WHERE title_action IS NOT NULL
                AND date_action >= now() at time zone 'utc'
    """, [util.ref(cr, 'mail.mail_activity_data_todo')])
