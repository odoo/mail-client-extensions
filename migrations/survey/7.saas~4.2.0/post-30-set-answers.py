# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    if util.table_exists(cr, 'survey'):
        return

    # Swap the matrix rows/cols according to change in new version
    # For 'matrix' type
    util.create_column(cr, 'survey_label','old_answer_id','integer')
    cr.execute("""insert into survey_label(old_answer_id, question_id_2, sequence, value, create_uid, create_date, write_date, write_uid) select a.id, a.question_id, a.sequence, a.answer, a.create_uid, a.create_date, a.write_date, a.write_uid
                from survey_answer a, survey_question q where a.question_id = q.id and q.type='matrix'""")
    util.create_column(cr, 'survey_label','old_column_id','integer')
    cr.execute("""insert into survey_label(old_column_id, question_id, value, create_uid, create_date, write_date, write_uid) select cl.id, cl.question_id, cl.title, cl.create_uid, cl.create_date, cl.write_date, cl.write_uid
                from survey_question_column_heading cl, survey_question q where cl.question_id = q.id and q.type='matrix'""")

    # For 'multiple' answer type
    cr.execute("""insert into survey_label(old_answer_id, question_id, sequence, value, create_uid, create_date, write_date, write_uid) select a.id, a.question_id, a.sequence, a.answer, a.create_uid, a.create_date, a.write_date, a.write_uid
                from survey_answer a, survey_question q where a.question_id = q.id and q.type!='matrix'""")
