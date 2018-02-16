# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_record(cr, 'marketing_automation.ir_cron_marketing_campaign_every_hour')
    util.remove_record(cr, 'marketing_automation.ir_cron_marketing_campaign_every_day')

    # TODO remove test campaigns?

    # ==============================
    # == activities
    # ==============================
    util.rename_model(cr, 'marketing.campaign.activity', 'marketing.activity')

    util.rename_field(cr, 'marketing.activity', 'object_id', 'model_id')
    util.create_column(cr, 'marketing_activity', 'utm_source_id', 'int4')
    util.create_column(cr, 'marketing_activity', 'trigger_type', 'varchar')
    util.create_column(cr, 'utm_source', '_ma_id', 'int4')
    cr.execute("""
      WITH new_src AS (
        INSERT INTO utm_source(_ma_id, name)
             SELECT id, name
               FROM marketing_activity
          RETURNING id, _ma_id
      )
      UPDATE marketing_activity a
         SET utm_source_id = n.id,
             trigger_type = CASE WHEN start THEN 'begin' ELSE 'act' END
        FROM new_src n
       WHERE n._ma_id = a.id
    """)
    util.remove_column(cr, 'marketing_activity', 'name')
    util.remove_column(cr, 'utm_source', '_ma_id')
    util.rename_field(cr, 'marketing.activity', 'action_type', 'activity_type')
    util.remove_column(cr, 'marketing_activity', 'start')

    util.create_column(cr, 'marketing_activity', 'mass_mailing_id', 'int4')
    # TODO create a massmailing FROM email_template_id
    # TODO report_id -> server action to generate report (side effect of save it on the record)
    # TODO 

    # reorganize activity tree using transitions...
    # cr.execute("SELECT id FROM marketing_activity WHERE start")


    # ==============================
    # == campaigns
    # ==============================
    util.rename_field(cr, 'marketing.campaign', 'object_id', 'model_id')
    util.create_column(cr, 'marketing_campaign', 'utm_campaign_id', 'int4')
    util.create_column(cr, 'marketing_campaign', 'active', 'boolean')
    util.create_column(cr, 'marketing_campaign', 'domain', 'varchar')
    util.create_column(cr, 'marketing_campaign', 'model_name', 'varchar')
    util.create_column(cr, 'marketing_campaign', 'last_sync_date', 'timestamp without time zone')
    util.remove_field(cr, 'marketing.campaign', 'mode')

    cr.execute("""
      WITH segments AS (
            SELECT s.campaign_id,
                   (array_agg(s.id order by s.id))[1] as segid,
                   (array_agg(f.domain order by s.id))[1] as domain,
                   (array_agg(s.id order by s.id))[2:count(s.id)] as others
              FROM marketing_campaign_segment s
         LEFT JOIN ir_filters f ON (f.id = s.ir_filter_id)
          GROUP BY s.campaign_id
      ),
      _upd_main AS (
        UPDATE marketing_campaign c
           SET last_sync_date = s.sync_last_date,
               domain = g.domain,
               state = CASE WHEN c.state = 'running' THEN s.state ELSE c.state END
          FROM segments g, marketing_campaign_segment s
         WHERE c.id = g.campaign_id
           AND s.id = g.segid
      ),
      _to_copy AS (
        SELECT campaign_id, unnest(others) as segment_id
          FROM segments
      )
      INSERT INTO marketing_campaign (name, last_sync_date, domain, state,
                                      model_id, unique_field_id)
          SELECT CONCAT(c.name, ' (', s.name, ')'),
                 s.sync_last_date,
                 f.domain,
                 CASE WHEN c.state = 'running' THEN s.state ELSE c.state END,
                 c.model_id, c.unique_field_id
            FROM _to_copy t
            JOIN marketing_campaign c ON (t.campaign_id = c.id)
            JOIN marketing_campaign_segment s ON (t.segment_id = s.id)
       LEFT JOIN ir_filters f ON (f.id = s.ir_filter_id)
    """)

    # duplicate activities -> 


    util.create_column(cr, 'utm_campaign', '_mc_id', 'int4')
    cr.execute("""
      WITH new_utm AS (
        INSERT INTO utm_campaign(_mc_id, name)
             SELECT id, name
               FROM marketing_campaign
          RETURNING id, _mc_id
      )
      UPDATE marketing_campaign c
         SET utm_campaign_id = n.id
        FROM new_utm n
       WHERE n._mc_id = c.id
    """)

    cr.execute("""
        UPDATE marketing_campaign c
           SET active = true,
               model_name = m.model,
               state = CASE WHEN c.state IN ('cancelled', 'done') THEN 'stopped' ELSE c.state END,
               domain = CASE WHEN c.domain IS NULL THEN '[]' ELSE c.domain END
          FROM ir_model m
         WHERE m.id = c.model_id
    """)

    util.remove_column(cr, 'marketing_campaign', 'name')
    util.remove_column(cr, 'utm_campaign', '_mc_id')

    old_fields = util.splitlines("""
        partner_field_id
        fixed_cost
        segments_count
    """)
    for f in old_fields:
        util.remove_field(cr, 'marketing.campaign', f)

    util.rename_field(cr, 'marketing.campaign', 'activity_ids', 'marketing_activity_ids')

    # workitem -> participant + trace
    # cr.execute("
    #     CREATE TABLE marketing_participant
    # ")
    # cr.execute("""
    #     INSERT INTO ()
    # """)

    # cleanup
    util.remove_model(cr, 'marketing.campaign.segment')
    util.remove_model(cr, 'marketing.campaign.workitem')
