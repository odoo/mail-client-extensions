# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "survey_survey", "state", "varchar")

    cr.execute(
        """
        UPDATE survey_survey s
           SET state = CASE WHEN g.closed=true OR s.stage_id=%s THEN 'closed'
                            WHEN s.stage_id=%s THEN 'open'
                            ELSE 'draft'
                        END
          FROM survey_stage g
         WHERE g.id = s.stage_id
    """,
        [util.ref(cr, "survey.stage_closed"), util.ref(cr, "survey.stage_in_progress")],
    )
    cr.execute("UPDATE survey_survey SET state = 'draft' WHERE state IS NULL")

    util.remove_model(cr, "survey.stage")

    util.remove_view(cr, "survey.survey_web_assets")
    util.remove_view(cr, "survey.assets_common")
