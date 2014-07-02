# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    if util.table_exists(cr, 'survey'):
        return

    cr.execute("select max(id) from survey_question")
    max_ques_id = cr.fetchone() # Needed for targeting only new records

    cr.execute("update survey_question set validation_type = 'do_not_validate' where validation_type is null")

    map = {'do_not_validate' : "validation_required = 'f'",
           'must_be_specific_length': "validation_length_min = validation_minimum_no, validation_length_max = validation_maximum_no",
           'must_be_whole_number': "validation_min_float_value = validation_minimum_no, validation_max_float_value = validation_maximum_no",
           'must_be_decimal_number': "validation_min_float_value = validation_minimum_float, validation_max_float_value = validation_maximum_float",
           'must_be_date': "validation_min_date = validation_minimum_date, validation_max_date = validation_maximum_date",
           'must_be_email_address': "validation_email = 't', validation_required = 'f'" # because in old version only one option was possible
           }
    # Textboxes - copy values between columns in the same record. Select only old textboxes
    # AND Multiple Textboxes (now textbox)- copy values between parent columns to child record columns
    cr.execute("""select * from survey_question
                where id in (select id from survey_question
                where type = 'textbox' and id <= %s)
                or id in (select child.id from survey_question parent, survey_question child where parent.id = child.old_question_id
                and parent.type = 'multiple_textboxes' and child.id > %s)""", [max_ques_id, max_ques_id, ])
    recs = cr.dictfetchall()
    for rec in recs:
        update_sql = "update survey_question set "+map[rec['validation_type']]+" where validation_type= '"+rec['validation_type']+"' and id=%s"
        cr.execute(update_sql, [rec['id'], ])

    # Turn on validations by changing type. Change type only if there is a validation, else format of input is unexpected.
    cr.execute("""update survey_question set type = 'numerical_box' where type = 'textbox'
                and validation_required = 't' and validation_type in ('must_be_whole_number', 'must_be_decimal_number')""")
    cr.execute("""update survey_question set type = 'datetime' where type = 'textbox'
                and validation_required = 't' and validation_type in ('must_be_date')""")