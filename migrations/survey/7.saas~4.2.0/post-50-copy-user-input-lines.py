# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    if util.table_exists(cr, 'survey'):
        return

    # Copy survey_response_line (old) to survey_user_input_line (new)
    cr.execute("select max(id) from survey_user_input_line")
    max_input_line_id = cr.fetchone() # Needed for targeting only new records during updating answer values

    util.create_column(cr, 'survey_user_input_line','old_rl_id','integer')

    type_map = {'free_text': 'free_text',
                'textbox': 'text',
                'numerical_box': 'number',
                'datetime': 'date',
                'simple_choice': 'suggestion',
                'multiple_choice': 'suggestion',
                'matrix': 'suggestion',
                }
    args_list = [(t, s) for t, s in type_map.items()]

    whens = " WHEN q.type = %s THEN %s " * len(type_map)

    # Create user_input_lines without values
    cr.execute("""insert into survey_user_input_line(old_rl_id, user_input_id, question_id, date_create, survey_id, skipped, answer_type, create_uid, create_date, write_date, write_uid)
                select rl.id, ui.id, rl.question_id, rl.date_create, ui.survey_id, CASE WHEN rl.state='skip' THEN 't'::bool ELSE 'f'::bool END, CASE {whens} END, rl.create_uid, rl.create_date, rl.write_date, rl.write_uid
                from survey_response_line rl, survey_user_input ui, survey_question q
                where ui.old_response_id=rl.response_id and rl.question_id=q.id""".format(whens=whens), [a for b in args_list for a in b])

    # For multi_choice answers - each response answer is converted to user_input_line
    cr.execute("""insert into survey_user_input_line(old_rl_id, user_input_id, question_id, date_create, survey_id, skipped, answer_type, value_suggested, create_uid, create_date, write_date, write_uid)
                select rl.id, ui.id, rl.question_id, rl.date_create, ui.survey_id, CASE WHEN rl.state='skip' THEN 't'::bool ELSE 'f'::bool END, 'suggestion', l.id, rl.create_uid, rl.create_date, rl.write_date, rl.write_uid
                from survey_response_line rl, survey_user_input ui, survey_question q, survey_response_answer ra, survey_label l, survey_answer a
                where ui.old_response_id=rl.response_id and rl.question_id=q.id and ra.response_id = rl.id and l.old_answer_id = a.id and a.id = ra.answer_id
                and q.type='multiple_choice'""")

    # For multi-answer questions that were converted into separate questions, create corresponding separate response_lines
    whens = " WHEN qn.type = %s THEN %s " * len(type_map)
    cr.execute("""insert into survey_user_input_line(old_rl_id, user_input_id, question_id, date_create, survey_id, skipped, answer_type, create_uid, create_date, write_date, write_uid)
                select rl.id, ui.id, qn.id, rl.date_create, ui.survey_id, CASE WHEN rl.state='skip' THEN 't'::bool ELSE 'f'::bool END, CASE {whens} END, rl.create_uid, rl.create_date, rl.write_date, rl.write_uid
                from survey_response_line rl, survey_user_input ui, survey_question q, survey_question qn
                where ui.old_response_id=rl.response_id and rl.question_id=q.id and qn.old_question_id=q.id""".format(whens=whens), [a for b in args_list for a in b])

    cr.execute("delete from survey_user_input_line where question_id in (select distinct(old_question_id) from survey_question where old_question_id is not null)")

    # survey_response_line has many answers, but only one comment.
    # Need to convert comment into new response_line whose answer_type will be text

    # Non-free_text type questions
    cr.execute("""insert into survey_user_input_line(user_input_id, question_id, date_create, survey_id, skipped, answer_type, value_text, create_uid, create_date, write_date, write_uid)
                select ui.id, rl.question_id, rl.date_create, ui.survey_id, CASE WHEN rl.state='skip' THEN 't'::bool ELSE 'f'::bool END, 'text', rl.comment, rl.create_uid, rl.create_date, rl.write_date, rl.write_uid
                from survey_response_line rl, survey_user_input ui, survey_question q
                where ui.old_response_id=rl.response_id and q.id = rl.question_id
                and rl.comment is not null and q.type != 'free_text'""")

    # free_text type questions, only update
    cr.execute("""update survey_user_input_line uil set value_free_text = rl.comment
                from survey_response_line rl, survey_user_input ui, survey_question q
                where ui.old_response_id=rl.response_id and q.id = rl.question_id and uil.old_rl_id = rl.id
                and rl.comment is not null and q.type = 'free_text'""")

    # For non-'suggestion' type answers
    def get_datatype(column_name):
        cr.execute("SELECT data_type FROM information_schema.columns WHERE table_name = 'survey_user_input_line' and column_name= %s", [column_name, ])
        dt = cr.fetchone()[0]
        return dt

    cr.execute("select * from survey_user_input_line where id > %s and answer_type != 'suggestion'", [max_input_line_id, ])
    records = cr.dictfetchall()
    for uil in records:
        cr.execute("""update survey_user_input_line uil set value_{ans_type}= ra.answer::{dt}
                    from survey_response_answer as ra, survey_response_line rl, survey_answer a
                    where uil.id = %s
                    and uil.question_id = a.new_question_id and ra.answer_id = a.id
                    and uil.old_rl_id = rl.id
                    and rl.id = ra.response_id""".format(ans_type=uil['answer_type'], dt=get_datatype('value_'+uil['answer_type'])), [uil['id'], ])

    # For split-converted questions
    cr.execute("""update survey_user_input_line uil set value_text = ra.answer
                from survey_response_answer ra, survey_answer a, survey_response_line rl
                where uil.question_id = a.new_question_id
                and ra.answer_id = a.id and uil.old_rl_id = rl.id and ra.response_id = rl.id""")

    # For matrix-type. Create user_input_lines with their actual answers
    cr.execute("""insert into survey_user_input_line (user_input_id, question_id, date_create, survey_id, skipped, answer_type, value_suggested, value_suggested_row, create_uid, create_date, write_date, write_uid)
                select uil.user_input_id, uil.question_id, uil.date_create, uil.survey_id, uil.skipped, uil.answer_type, lc.id, la.id, rl.create_uid, rl.create_date, rl.write_date, rl.write_uid
                from survey_user_input_line uil, survey_response_answer ra, survey_response_line rl, survey_label la, survey_label lc
                where uil.old_rl_id = rl.id and ra.response_id=rl.id
                and la.old_answer_id = ra.answer_id and lc.old_column_id = ra.column_id
                and ra.column_id is not null""")

    # simple_choice - Records are already inserted, so only need to update
    cr.execute("""update survey_user_input_line uil
                set value_suggested = l.id
                from survey_response_line rl, survey_response_answer ra, survey_answer a, survey_label l, survey_question q
                where uil.old_rl_id = rl.id and ra.response_id = rl.id and ra.answer_id = a.id and a.id = l.old_answer_id and rl.question_id = q.id
                and uil.answer_type='suggestion' and q.type = 'simple_choice'""")

    #Now delete the extra user_input_line records for multi_choice answers (and split answers)
    cr.execute("delete from survey_user_input_line where answer_type = 'suggestion' and value_suggested is null and skipped = 'f'")

    # For simple textboxes
    cr.execute("""update survey_user_input_line uil set value_text = rl.single_text
                from survey_response_line rl where rl.id = uil.old_rl_id
                and uil.answer_type = 'text' and uil.value_text is null and uil.skipped = 'f'
                and rl.single_text is not null""")
