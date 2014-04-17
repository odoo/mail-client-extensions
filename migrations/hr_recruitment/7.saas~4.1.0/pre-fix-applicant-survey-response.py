# -*- coding: utf-8 -*-

def migrate(cr, version):
    # in saas-3, the field `response was in fact a m2o to a response (user input)
    # remove wrong references...
    cr.execute("""UPDATE hr_applicant a
                     SET response = NULL
                   WHERE NOT EXISTS(SELECT 1
                                      FROM survey_user_input
                                     WHERE id = a.response)
               """)
