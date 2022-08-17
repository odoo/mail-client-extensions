# -*- coding: utf-8 -*-
import os

from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):

    # There is no longer a form and inbound tree view for phonecall whether or not crm_voip will be installed
    util.remove_view(cr, 'crm.crm_case_phone_form_view')
    util.remove_view(cr, 'crm.crm_case_inbound_phone_tree_view')

    cr.execute("SELECT value FROM ir_config_parameter WHERE key='migration.crm.want_voip'")
    want = cr.fetchone()
    if want:
        util.force_install_module(cr, 'voip')
        util.force_install_module(cr, 'crm_voip')

    if util.module_installed(cr, 'crm_voip'):
        util.remove_record(cr, 'crm.filter_crm_phonecall_sales_team')
        util.remove_record(cr, 'crm.filter_crm_phonecall_phone_call_to_do')

        # The phonecall tree, calendar and filter view are renamed in the crm_voip module
        util.rename_xmlid(cr, 'crm.crm_case_phone_tree_view', 'crm_voip.crm_phonecall_tree_view')
        util.rename_xmlid(cr, 'crm.crm_case_phone_calendar_view', 'crm_voip.crm_phonecall_calendar_view')
        util.rename_xmlid(cr, 'crm.view_crm_case_phonecalls_filter', 'crm_voip.view_crm_case_phonecalls_filter')
        util.rename_xmlid(cr, 'crm.phonecall_to_phonecall_view', 'crm_voip.phonecall_to_phonecall_view')
        util.remove_view(cr, 'crm_voip.overide_phonecall_to_phonecall_view')
        return

    # If crm_voip will not be installed, then we can delete these phonecall views as well.
    util.remove_view(cr, 'crm.crm_case_phone_tree_view')
    util.remove_view(cr, 'crm.crm_case_phone_calendar_view')
    util.remove_view(cr, 'crm.view_crm_case_phonecalls_filter')
    util.remove_view(cr, 'crm.phonecall_to_phonecall_view')

    cr.execute("SELECT count(1) from crm_phonecall")
    if not cr.fetchone()[0]:
        return  # nothing to do...

    cr.execute("SELECT id FROM ir_module_module WHERE name='crm_voip'")
    [voip_id] = cr.fetchone() or [None]
    if voip_id:
        message = """

# Note about your Phonecalls

Your phonecalls have been converted to comments on the related lead/opportunities.
If you are using these phonecalls as a call center, you may want to install the [VOIP](/web#id=%d&view_type=form&model=ir.module.module) App.
[Contact us](mailto:online@odoo.com) if you want to avoid the conversion to comments.
""" % voip_id

        util.announce(cr, '9.0', message, format='md', header=None)

    env = util.env(cr)
    activity = env.ref('crm.crm_activity_data_call')
    stg_new = util.ref(cr, 'crm.stage_lead1')
    stg_done = util.ref(cr, 'crm.stage_lead5')

    stg_dead = env['crm.stage'].search([('type', 'in', ['lead', 'both']), ('probability', '=', 0)],
                                       order='fold desc, sequence desc', limit=1)
    if not stg_dead:
        stg_dead = env['crm.stage'].create({
            'name': 'Dead',
            'type': 'lead',
            'probability': 0,
            'sequence': 999,
            'fold': True,
        })
    stg_dead = stg_dead.id

    if not os.environ.get('ODOO_MIG_9_NO_ORPHAN_PHONECALL'):
        team_col = 'team_id' if util.column_exists(cr, 'crm_phonecall', 'team_id') else 'section_id'
        cr.execute("""
        WITH new_leads AS (
            INSERT INTO crm_lead(create_date, create_uid, name, partner_id, team_id, user_id, description, priority,
                                phone, mobile, active, type,stage_id, message_bounce)
                SELECT create_date, create_uid, 'Phonecall', partner_id, {0}, user_id, description, priority,
                        partner_phone, partner_mobile, active,
                        case when state = 'done' then 'opportunity' else 'lead' end,
                        case when state = 'done' then %s when state = 'cancel' then %s else %s end,
                        id
                FROM crm_phonecall
                WHERE opportunity_id IS NULL
                ORDER BY id
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
        """.format(team_col), [stg_done, stg_dead, stg_new])

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
               WHERE p.opportunity_id IS NOT NULL
           GROUP BY 1, 2
      )
      UPDATE crm_lead_tag t
         SET color = 0
        FROM new_tags n
       WHERE t.id = n.id
    """)

    cr.execute("""
        INSERT INTO mail_message(create_date, create_uid, model, res_id, date, message_type, body, subtype_id)
        SELECT create_date, create_uid, 'crm.lead', opportunity_id, date, 'comment',
               concat('Phonecall (',
                      to_char(to_timestamp((coalesce(duration, 0)) * 60), 'MI:SS'),
                      ' min): ',
                      name),
               %s
          FROM crm_phonecall
          WHERE opportunity_id IS NOT NULL
    """, [activity.subtype_id.id])

    # util.delete_model(cr, 'crm.phonecall')
    # util.delete_model(cr, 'crm.phonecall.category')
