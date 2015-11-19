# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    cr.execute("SELECT value FROM ir_config_parameter WHERE key='migration.crm.want_voip'")
    want = cr.fetchone()
    if want:
        util.force_install_module(cr, 'voip')
        util.force_install_module(cr, 'crm_voip')
        util.remove_record(cr, 'crm.filter_crm_phonecall_sales_team')
        util.remove_record(cr, 'crm.filter_crm_phonecall_phone_call_to_do')
        return

    cr.execute("SELECT count(1) from crm_phonecall")
    if not cr.fetchone()[0]:
        return  # nothing to do...

    cr.execute("SELECT id FROM ir_module_module WHERE name='crm_voip'")
    [voip_id] = cr.fetchone() or [None]
    if voip_id:
        message = """

# Note about your Phonecalls

Your phonecalls have been converted to comments on the related lead/opportunities.
If you are using these phonecalls as a call center, you may want to install the [VOIP](/web#id=%d&view_type=form&model=ir.module.module) Application.
[Contact us](mailto:online@odoo.com) if you want to avoid the conversion to comments.
""" % voip_id

        util.announce(cr, '9.0', message, format='md', header=None)

    env = util.env(cr)

    activity = env.ref('crm.crm_activity_data_call')
    stg_new = util.ref(cr, 'crm.stage_1')

    stg_dead = env['crm.stage'].search([('type', 'in', ['lead', 'both']),
                                        ('probability', '=', 0),
                                        ('fold', '=', True)])[0].id
    stg_done = env['crm.stage'].search([('type', '=', 'opportunity')], order='sequence')[0].id

    cr.execute("""
      WITH new_leads AS (
        INSERT INTO crm_lead(name, partner_id, team_id, user_id, description, priority,
                             phone, mobile, active, type,stage_id, message_bounce)
             SELECT 'Phonecall', partner_id, team_id, user_id, description, priority,
                    partner_phone, partner_mobile, active,
                    case when state = 'done' then 'opportunity' else 'lead' end,
                    case when state = 'done' then %s when state = 'cancel' then %s else %s end,
                    id
               FROM crm_phonecall
              WHERE opportunity_id IS NULL
          RETURNING id, message_bounce as call_id
      ),
      _1 AS (
        UPDATE crm_phonecall c
           SET opportunity_id = l.id
          FROM new_leads l
         WHERE c.id = l.call_id
      )
      UPDATE crm_lead l
         SET message_bounce = 0
        FROM new_leads n
       WHERE l.id = n.id
    """, [stg_done, stg_dead, stg_new])

    cr.execute("""
      WITH new_tags AS (
        INSERT INTO crm_lead_tag(name, team_id, color)
             SELECT concat('Phonecall: ', name), team_id, id
               FROM crm_phonecall_category c
              WHERE EXISTS (SELECT 1 FROM crm_phonecall WHERE categ_id=c.id)
          RETURNING id, color as categ_id
      ),
      _1 AS (
        INSERT INTO crm_lead_tag_rel (lead_id, tag_id)
             SELECT p.opportunity_id, t.id
               FROM crm_phonecall p
               JOIN new_tags t ON (t.categ_id = p.categ_id)
           GROUP BY 1, 2
      )
      UPDATE crm_lead_tag t
         SET color = 0
        FROM new_tags n
       WHERE t.id = n.id
    """)

    cr.execute("""
        INSERT INTO mail_message(model, res_id, date, message_type, body, subtype_id)
        SELECT 'crm.lead', opportunity_id, date, 'comment',
               concat('Phonecall (',
                      replace(format('%%2s', trunc(duration)::varchar), ' ', '0'),
                      ':',
                      coalesce(lpad(trunc(60 * (duration::decimal %% 1))::varchar, 2, '0'), '00'),
                      ' min): ',
                      name),
               %s
          FROM crm_phonecall
    """, [activity.subtype_id.id])

    # util.delete_model(cr, 'crm.phonecall')
    # util.delete_model(cr, 'crm.phonecall.category')
