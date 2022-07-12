# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):

    cr.execute(
        """
            DELETE FROM hr_department_mail_channel_rel hdmc
                  USING mail_channel mc
                  WHERE hdmc.mail_channel_id = mc.id
                    AND mc.channel_type != 'channel'
        """
    )

    util.remove_field(cr, "hr.job", "state")
    util.remove_record(cr, "hr.menu_config_plan_types")

    # Convert m2m to m2o
    util.create_column(cr, "hr_plan_activity_type", "plan_id", "int4")

    cr.execute(
        """
            WITH no_dupes AS (
                SELECT hr_plan_activity_type_id, min(hr_plan_id) AS hr_plan_id
                  FROM hr_plan_hr_plan_activity_type_rel
              GROUP BY hr_plan_activity_type_id
                HAVING COUNT(hr_plan_activity_type_id) = 1
            ),
            _ AS (
                DELETE FROM hr_plan_hr_plan_activity_type_rel r
                      USING no_dupes d
                      WHERE d.hr_plan_id = r.hr_plan_id
                        AND d.hr_plan_activity_type_id = r.hr_plan_activity_type_id
            )
            UPDATE hr_plan_activity_type act
               SET plan_id = d.hr_plan_id
              FROM no_dupes d
             WHERE act.id = d.hr_plan_activity_type_id
        """
    )

    pa_cols = util.get_columns(cr, "hr_plan_activity_type", ("id", "plan_id"))
    pa_pref_cols = [f"p.{c}" for c in pa_cols]
    cr.execute(
        f"""
            WITH plan_activities AS (
                SELECT hr_plan_activity_type_id, ARRAY_AGG(hr_plan_id ORDER BY hr_plan_id) AS plans
                  FROM hr_plan_hr_plan_activity_type_rel
              GROUP BY hr_plan_activity_type_id
            ),
            _upd AS (
                UPDATE hr_plan_activity_type a
                   SET plan_id = pa.plans[1]
                  FROM plan_activities pa
                 WHERE pa.hr_plan_activity_type_id = a.id
            )
            INSERT INTO hr_plan_activity_type({','.join(pa_cols)}, plan_id)
                 SELECT {','.join(pa_pref_cols)}, UNNEST(pa.plans[2:])
                   FROM hr_plan_activity_type p
                   JOIN plan_activities pa
                     ON p.id = pa.hr_plan_activity_type_id
        """
    )

    cr.execute("DROP TABLE hr_plan_hr_plan_activity_type_rel")
