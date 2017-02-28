# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # convert crm.activity to mail.activity.type
    util.create_column(cr, 'mail_activity_type', '_caid', 'int4')
    cr.execute("""
        INSERT INTO mail_activity_type(_caid, name, sequence, icon, summary, days, res_model_id)
             SELECT a.id, s.name, a.sequence, 'fa-tasks', s.description, a.days,
                    (SELECT id FROM ir_model WHERE model='crm.lead')
               FROM crm_activity a
               JOIN mail_message_subtype s ON (s.id = a.subtype_id)
          RETURNING _caid, id
    """)

    for caid, maid in cr.fetchall():
        util.replace_record_references(cr, ('crm.activity', caid), ('mail.activity.type', maid))

    # create activities
    cr.execute("""
        INSERT INTO mail_activity(activity_type_id, user_id,
                                  res_model_id, res_id, res_model, res_name,
                                  summary, date_deadline)
             SELECT ma.id, COALESCE(l.user_id,
                                    -- Use the team leader if admin was the last to modify the lead
                                    CASE WHEN COALESCE(l.write_uid, l.create_uid, 1) = 1
                                         THEN t.user_id
                                     END,
                                    l.write_uid,
                                    l.create_uid,
                                    1),
                    ma.res_model_id, l.id, 'crm.lead', l.name,
                    l.title_action, COALESCE(l.date_action, l.write_date, l.create_date)
               FROM crm_lead l
               JOIN mail_activity_type ma ON (ma._caid = l.next_activity_id)
               LEFT JOIN crm_team t ON (t.id = l.team_id)
    """)

    util.rename_field(cr, 'crm.lead', 'date_action', 'activity_date_deadline')

    fields_refs = {
        'next_activity_id': 'activity_ids',
        'date_action_next': 'activity_date_deadline',
        'date_action_last': 'write_date',       # no better alternative...
        'title_action': 'activity_summary',
    }
    for old, new in fields_refs.items():
        util.update_field_references(cr, old, new, only_models=['crm.lead'])

    util.remove_column(cr, 'mail_activity_type', '_caid')
    util.delete_model(cr, 'crm.activity')
    util.delete_model(cr, 'crm.activity.log')
