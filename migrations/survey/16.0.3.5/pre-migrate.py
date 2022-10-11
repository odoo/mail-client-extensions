# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute(
        """
        UPDATE survey_question
           SET question_type = NULL
         WHERE is_page IS TRUE
        """
    )
