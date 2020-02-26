# -*- coding: utf-8 -*-


def migrate(cr, version):
    # prepare new constraint
    cr.execute("""
        UPDATE survey_survey
           SET scoring_success_min = 0
         WHERE COALESCE(scoring_success_min, 0) NOT BETWEEN 0 AND 100
    """)
