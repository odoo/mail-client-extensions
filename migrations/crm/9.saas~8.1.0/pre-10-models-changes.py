# -*- coding: utf-8 -*-
import os
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'crm_stage', 'team_id', 'int4')
    util.create_column(cr, 'crm_stage', '_tmp', 'int4')
    cols = util.get_columns(cr, 'crm_stage', ('id', 'team_id', '_tmp'))
    s_cols = ",".join("s." + c for c in cols)
    cols = ",".join(cols)

    cr.execute("""
        WITH only_one_team AS (
            SELECT stage_id, (array_agg(team_id))[1] as team_id
              FROM crm_team_stage_rel
          GROUP BY 1
            HAVING count(team_id) = 1
        ),
        _ AS (
            DELETE FROM crm_team_stage_rel r
                  USING only_one_team o
                  WHERE r.team_id=o.team_id
                    AND r.stage_id=o.stage_id
        )
        UPDATE crm_stage s
           SET team_id = o.team_id
          FROM only_one_team o
         WHERE s.id = o.stage_id
    """)

    act = os.environ.get('ODOO_MIG_S8_CRM_STAGE', 'share')
    # 2 valid values: 'duplicate', 'share'

    if act == 'duplicate':
        cr.execute("""
            WITH stage_teams AS (
                SELECT stage_id, array_agg(team_id order by team_id) as teams
                  FROM crm_team_stage_rel
              GROUP BY 1
                HAVING array_agg(team_id order by team_id) != (SELECT array_agg(id order by id) FROM crm_team WHERE active)
                   AND array_agg(team_id order by team_id) != (SELECT array_agg(id order by id) FROM crm_team)
            ),
            _upd AS (
              UPDATE crm_stage s
                 SET team_id = t.teams[1]
                FROM stage_teams t
               WHERE t.stage_id = s.id
            ),
            new_stages AS (
                INSERT INTO crm_stage({cols}, team_id, _tmp)
                     SELECT {s_cols}, unnest(t.teams[2:array_length(t.teams, 1)]), s.id
                       FROM crm_stage s
                       JOIN stage_teams t ON (s.id = t.stage_id)
                  RETURNING id, team_id, _tmp
            )

            -- reassign lead to correct stage depending on team
            -- users may seen duplicated stage in kanban view depending on lead team
            UPDATE crm_lead l
               SET stage_id = n.id
              FROM new_stages n
             WHERE l.stage_id = n._tmp
               AND l.team_id = n.team_id
        """.format(**locals()))

    elif act != 'share':
        raise util.MigrationError('Invalid environment variable: $ODOO_MIG_S8_CRM_STAGE=%s' % act)

    util.remove_column(cr, 'crm_stage', '_tmp')

    # force no update on data
    xids = "1235"
    if not util.ref(cr, 'crm.stage_lead4'):
        util.rename_xmlid(cr, 'crm.stage_lead5', 'crm.stage_lead4')
        xids += '4'
    xids = ['stage_lead' + x for x in xids]
    xids += ['crm_stage_2_' + x for x in '1234']    # demo data

    cr.execute("""
        UPDATE ir_model_data
           SET noupdate = true
         WHERE module='crm'
           AND name IN %s
    """, [tuple(xids)])

    if util.table_exists(cr, 'crm_activity'):
        # activities m2m
        util.create_m2m(cr, 'crm_activity_rel', 'crm_activity', 'crm_activity',
                        'activity_id', 'recommended_id')
        cr.execute("""
            INSERT INTO crm_activity_rel(activity_id, recommended_id)
                 SELECT id, activity_1_id FROM crm_activity WHERE activity_1_id IS NOT NULL
                 UNION
                 SELECT id, activity_2_id FROM crm_activity WHERE activity_2_id IS NOT NULL
                 UNION
                 SELECT id, activity_3_id FROM crm_activity WHERE activity_3_id IS NOT NULL
        """)
