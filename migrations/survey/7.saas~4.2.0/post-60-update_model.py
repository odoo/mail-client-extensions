# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # stage -> stage_id

    if util.table_exists(cr, 'survey'):
        # This means the model wasn't renamed and hence no adaptation took place
        # This also implies survey related tables have no old data, hence do nothing
        return

    close_id = util.ref(cr, 'survey.stage_closed')
    inprog_id = util.ref(cr, 'survey.stage_in_progress')
    draft_id = util.ref(cr, 'survey.stage_draft')

    cr.execute("""UPDATE survey_survey s
                     SET stage_id = CASE WHEN state IN ('close', 'cancel')
                                         THEN %s
                                         WHEN EXISTS(SELECT 1
                                                       FROM survey_user_input
                                                      WHERE survey_id = s.id)
                                         THEN %s
                                         ELSE %s
                                     END
                """, (close_id, inprog_id, draft_id))

    util.remove_field(cr, "survey.survey", "state")

    # description are in html now
    for tbl in ['survey', 'page', 'question']:
        cr.execute("""UPDATE survey_{0}
                         SET description = {1}
                       WHERE description IS NOT NULL
                   """.format(tbl, util.pg_text2html('description')))
