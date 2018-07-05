# -*- coding: utf-8 -*-

def migrate(cr, version):
    cr.execute("ALTER TABLE survey_user_input DROP CONSTRAINT survey_user_input_deadline_in_the_past")
