# -*- coding: utf-8 -*-


def migrate(cr, version):
    # Satisfy the newly added constraints `triggered_questions_have_triggering_answer`
    # and `conditional_questions_have_triggering_question`.
    cr.execute(
        """
        UPDATE survey_question
           SET is_conditional = FALSE,
               triggering_question_id = NULL,
               triggering_answer_id = NULL
         WHERE is_conditional IS NOT TRUE
            OR triggering_question_id IS NULL
            OR triggering_answer_id IS NULL
        """
    )
