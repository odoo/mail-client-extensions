# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # convert crm.activity to mail.activity.type
    util.create_column(cr, 'mail_activity_type', '_caid', 'int4')

    id_map = {}
    name_map = dict(util.expand_braces(l) for l in util.splitlines("""
        {crm.crm,mail.mail}_activity_data_email
        {crm.crm,mail.mail}_activity_data_call
        {crm.crm,mail.mail}_activity_data_meeting

        crm.{crm,mail}_activity_demo_followup_quote
        crm.{crm,mail}_activity_demo_make_quote
        crm.{crm,mail}_activity_demo_call_demo
    """))
    for ca, mat in name_map.items():
        caid = util.ref(cr, ca)
        matid = util.ref(cr, mat)
        if caid and matid:
            id_map[caid] = matid
            cr.execute("UPDATE mail_activity_type SET _caid = %s WHERE id = %s", [caid, matid])

    if id_map:
        util.replace_record_references_batch(cr, id_map, "crm.activity", "mail.activity.type", replace_xmlid=False)

    cr.execute("""
        INSERT INTO mail_activity_type(_caid, name, sequence, icon, summary, days, res_model_id)
             SELECT a.id, s.name, a.sequence, 'fa-tasks', s.description, a.days,
                    (SELECT id FROM ir_model WHERE model='crm.lead')
               FROM crm_activity a
               JOIN mail_message_subtype s ON (s.id = a.subtype_id)
              WHERE a.id != ALL(%s)
          RETURNING _caid, id
    """, [list(id_map)])

    id_map = dict(cr.fetchall())
    if id_map:
        util.replace_record_references_batch(cr, id_map, "crm.activity", "mail.activity.type")

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
                    (SELECT id FROM ir_model WHERE model='crm.lead'),
                    l.id, 'crm.lead', l.name,
                    l.title_action, COALESCE(l.activity_date_deadline, l.write_date, l.create_date)
               FROM crm_lead l
               JOIN mail_activity_type ma ON (ma._caid = l.next_activity_id)
               LEFT JOIN crm_team t ON (t.id = l.team_id)
    """)

    util.remove_column(cr, 'mail_activity_type', '_caid')
    util.delete_model(cr, 'crm.activity')
    util.delete_model(cr, 'crm.activity.log')
