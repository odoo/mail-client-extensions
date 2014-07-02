# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def clean(cr):
    if util.table_exists(cr, 'hr_evaluation_plan_phase'):
        cr.execute("alter table hr_evaluation_plan_phase alter column survey_id drop not null")
    # will delete all data in cascade
    cr.execute("DELETE FROM survey")

def migrate(cr, version):
    cr.execute("SELECT count(1) FROM survey_response")
    if not cr.fetchone()[0]:
        # not any responses... remove all
        clean(cr)
        return

    models = [
        'survey', 'survey.page', 'survey.question',
        'survey.question.column.heading', 'survey.answer'
    ]

    FROM = ' UNION '.join("""
                          SELECT count(1) c
                            FROM {table} s
                           WHERE NOT EXISTS(SELECT 1
                                             FROM ir_model_data
                                            WHERE model={model}
                                              AND res_id = s.id
                                              AND module IS NOT NULL)
                              OR (    write_date IS NOT NULL
                                  AND create_date IS NOT NULL
                                  AND write_date - create_date > interval '1 minute'
                                 )
    """.format(model="'"+model+"'", table=util.table_of_model(cr, model))
        for model in models)

    cr.execute("SELECT SUM(c) FROM (%s) f" % FROM)
    if not cr.fetchone()[0]:
        # not any changes... remove all
        clean(cr)
        return

    util.rename_model(cr, 'survey', 'survey.survey')

    # remove the xmlid of the column "state" to forbid the ORM to delete it.
    # We will need it in the "post-" script to map it to stages...
    cr.execute("DELETE FROM ir_model_data WHERE module=%s AND model=%s AND name=%s",
               ('survey', 'ir.model.field', 'field_survey_state'))

    cr.execute("DELETE FROM ir_model_data WHERE module=%s AND model=%s AND name=%s",
                   ('survey', 'ir.model.fields', 'field_survey_question_validation_type'))

    util.create_column(cr, 'survey_survey', 'res_model', 'varchar')
    cr.execute("""UPDATE survey_survey s
                     SET res_model = CASE WHEN t.code = 'Human Resources'
                                          THEN 'hr.applicant'
                                          WHEN t.code in ('Customer Feedback', 'Supplier Selection')
                                          THEN 'res.users'
                                          ELSE NULL
                                      END
                    FROM survey_type t
                   WHERE t.id = s.type
               """)

    # restrictive by default
    util.create_column(cr, 'survey_survey', 'auth_required', 'boolean')
    cr.execute("UPDATE survey_survey SET auth_required = 't'")

    # question
    question_types = {
        'free_text': ('comment', 'descriptive_text',),
        'textbox': ('single_textbox',),
        'numerical_box': ('numerical_textboxes',),
        'datetime': ('date', 'date_and_time',),
        'simple_choice': ('multiple_choice_only_one_ans',),
        'multiple_choice': ('multiple_choice_multiple_ans',),
        'matrix': ('rating_scale', 'matrix_of_choices_only_one_ans', 'matrix_of_choices_only_multi_ans',
                    'matrix_of_drop_down_menus', 'table'),
    }

    util.create_column(cr, 'survey_question', 'matrix_subtype', 'character varying')
    cr.execute("update survey_question set matrix_subtype = CASE WHEN type = 'matrix_of_choices_only_multi_ans' THEN 'multiple' ELSE 'simple' END")

    whens = " WHEN type IN %s THEN %s " * len(question_types)
    args_list = [(s, t) for t, s in question_types.items()]
    cr.execute("UPDATE survey_question SET type = CASE {whens} ELSE type END".format(whens=whens),
               [a for b in args_list for a in b])
