# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    if util.table_exists(cr, 'survey'):
        return

    # Some question types permit multiple answers in old version, but not in new.
    # Convert such answers to questions
    util.create_column(cr, 'survey_question','old_question_id','integer') # Need this later for user_inputs
    util.create_column(cr, 'survey_answer','new_question_id','integer') # Need this later for user_inputs 'answer'

    cr.execute("""select * from survey_answer where question_id in (select id from survey_question
                where type in ('multiple_textboxes_diff_type', 'multiple_textboxes', 'datetime', 'numerical_box'))""")
    multi_ans = cr.dictfetchall()

    insert_sql = """insert into survey_question(old_question_id, question, validation_required, validation_type,
                    validation_error_msg, constr_mandatory, constr_error_msg, page_id, comments_allowed,
                    comments_message, type, validation_minimum_no, validation_maximum_no, validation_minimum_float,
                    validation_maximum_float, validation_minimum_date, validation_maximum_date, sequence,
                    comment_count_as_answer, column_nb, display_mode, matrix_subtype, create_uid, create_date,
                    write_date, write_uid)
                    select q.id, q.question||' - '||a.answer, q.validation_required, q.validation_type,
                    q.validation_error_msg, q.constr_mandatory, q.constr_error_msg, q.page_id, q.comments_allowed,
                    q.comments_message,
                    CASE WHEN q.type='multiple_textboxes_diff_type' and a.type in ('char', 'email') THEN 'textbox'
                    WHEN q.type='multiple_textboxes_diff_type' and a.type in ('integer', 'float') THEN 'numerical_box'
                    WHEN q.type='multiple_textboxes_diff_type' and a.type in ('date', 'datetime') THEN 'datetime'
                    WHEN q.type='multiple_textboxes' THEN 'textbox'
                    ELSE q.type END,
                    q.validation_minimum_no, q.validation_maximum_no, q.validation_minimum_float, q.validation_maximum_float,
                    q.validation_minimum_date, q.validation_maximum_date, q.sequence, q.comment_count_as_answer, 12,
                    'columns', q.matrix_subtype, q.create_uid, q.create_date, q.write_date, q.write_uid
                    from survey_answer a, survey_question q where a.question_id = q.id and a.id=%s returning id"""

    for rec in multi_ans:
        cr.execute(insert_sql, [rec['id'], ])
        new_ques_id = cr.fetchone()[0]
        cr.execute("update survey_answer set new_question_id = %s where id = %s", [new_ques_id, rec['id'], ])
