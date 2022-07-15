# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # page -> question
    util.create_column(cr, "survey_question", "survey_id", "int4")
    util.create_column(cr, "survey_question", "is_page", "boolean")
    util.create_column(cr, "survey_question", "random_questions_count", "int4")
    util.create_column(cr, "survey_question", "validation_min_datetime", "timestamp without time zone")
    util.create_column(cr, "survey_question", "validation_max_datetime", "timestamp without time zone")

    util.rename_field(cr, "survey.question", "question", "title")
    cr.execute(
        """
        UPDATE survey_question q
           SET survey_id = p.survey_id,
               is_page = FALSE
          FROM survey_page p
         WHERE p.id = q.page_id
    """
    )
    cr.execute(
        """
        INSERT INTO survey_question(page_id, is_page, survey_id, title, description, sequence, question_type)
             SELECT id,
                    TRUE,
                    survey_id,
                    COALESCE(title, id::varchar),
                    description,
                    sequence,
                    'free_text'
               FROM survey_page
    """
    )

    # resequence pages
    cr.execute(
        """
        WITH allq AS (
            SELECT q.id, p.survey_id, p.sequence AS pseq, p.id pid,
                   CASE is_page WHEN TRUE THEN -2147483648 ELSE q.sequence END AS qseq
              FROM survey_question q
              JOIN survey_page p ON p.id = q.page_id
        ),
        reseq AS (
            SELECT id, row_number() OVER(PARTITION BY survey_id ORDER BY pseq, pid, qseq, id) AS seq
              FROM allq
        )
        UPDATE survey_question q
           SET sequence = r.seq
          FROM reseq r
         WHERE r.id = q.id
    """
    )

    # update fk
    cr.execute("ALTER TABLE survey_question DROP CONSTRAINT IF EXISTS survey_question_page_id_fkey")
    cr.execute("ALTER TABLE survey_question ALTER COLUMN page_id DROP NOT NULL")

    for table, column, fk, _ in util.get_fk(cr, "survey_page"):
        cr.execute("ALTER TABLE {} DROP CONSTRAINT {}".format(table, fk))
        cr.execute(
            """
            UPDATE {table} t
               SET {column} = q.id
              FROM survey_question q
             WHERE q.is_page
               AND q.page_id = t.{column}
        """.format(
                table=table, column=column
            )
        )

    cr.execute(
        """
        UPDATE survey_question q
           SET page_id = CASE WHEN NOT q.is_page THEN p.id END
          FROM survey_question p
         WHERE p.page_id = q.page_id
           AND p.is_page
    """
    )

    util.merge_model(cr, "survey.page", "survey.question")

    # labels
    util.rename_field(cr, "survey.label", "quizz_mark", "answer_score")
    util.create_column(cr, "survey_label", "is_correct", "boolean")
    cr.execute("UPDATE survey_label SET is_correct = (answer_score > 0)")

    # survey
    util.create_column(cr, "survey_survey", "questions_layout", "varchar")
    util.create_column(cr, "survey_survey", "questions_selection", "varchar")
    util.create_column(cr, "survey_survey", "category", "varchar")
    util.create_column(cr, "survey_survey", "access_mode", "varchar")
    util.create_column(cr, "survey_survey", "access_token", "varchar")
    util.create_column(cr, "survey_survey", "scoring_type", "varchar")
    util.create_column(cr, "survey_survey", "passing_score", "float8")
    util.create_column(cr, "survey_survey", "is_attemps_limited", "boolean")
    util.create_column(cr, "survey_survey", "attemps_limit", "int4")
    util.create_column(cr, "survey_survey", "is_time_limited", "boolean")
    util.create_column(cr, "survey_survey", "time_limit", "float8")
    util.create_column(cr, "survey_survey", "certificate", "boolean")
    util.create_column(cr, "survey_survey", "certification_mail_template_id", "int4")

    util.rename_field(cr, "survey.survey", "auth_required", "users_login_required")
    util.rename_field(cr, "survey.survey", "tot_sent_survey", "invite_count")
    util.rename_field(cr, "survey.survey", "tot_start_survey", "answer_count")
    util.rename_field(cr, "survey.survey", "tot_comp_survey", "answer_done_count")

    cr.execute(
        """
        UPDATE survey_survey
           SET questions_layout = 'page_per_section',
               questions_selection = 'all',
               category = 'default',
               access_mode = 'public',
               access_token = md5(concat(clock_timestamp()::varchar, ';', random()::varchar))::uuid::varchar,
               scoring_type = CASE quizz_mode WHEN TRUE THEN 'scoring_with_answers' ELSE 'no_scoring' END,
               passing_score = 80,
               is_attemps_limited = FALSE,
               attemps_limit = 1,
               is_time_limited = FALSE,
               certificate = FALSE
    """
    )

    util.remove_field(cr, "survey.survey", "public_url_html")
    util.remove_field(cr, "survey.survey", "print_url")
    util.remove_field(cr, "survey.survey", "result_url")
    util.remove_field(cr, "survey.survey", "quizz_mode")
    util.remove_field(cr, "survey.survey", "email_template_id")
    util.remove_field(cr, "survey.survey", "designed")

    # user_input
    util.create_column(cr, "survey_user_input", "invite_token", "varchar")
    util.create_column(cr, "survey_user_input", "quizz_passed", "boolean")
    util.rename_field(cr, "survey.user_input", "date_create", "start_datetime")
    cr.execute("ALTER TABLE survey_user_input ALTER COLUMN start_datetime DROP NOT NULL")
    cr.execute("UPDATE survey_user_input SET start_datetime = NULL WHERE state = 'new'")

    util.remove_field(cr, "survey.user_input", "print_url")
    util.remove_field(cr, "survey.user_input", "result_url")

    # user_input_line
    util.create_column(cr, "survey_user_input_line", "value_datetime", "timestamp without time zone")
    util.rename_field(cr, "survey.user_input_line", "quizz_mark", "answer_score")
    util.remove_field(cr, "survey.user_input_line", "date_create")

    # invite wizard
    util.rename_field(cr, "survey.invite", "multi_email", "emails")
    util.rename_field(cr, "survey.invite", "public_url", "survey_url")
    util.rename_field(cr, "survey.invite", "date_deadline", "deadline")
    cr.execute("ALTER TABLE survey_mail_compose_message_res_partner_rel RENAME TO survey_invite_partner_ids")
    cr.execute("ALTER TABLE survey_invite_partner_ids RENAME COLUMN wizard_id TO invite_id")
    util.create_column(cr, "survey_invite", "existing_mode", "varchar")
    cr.execute("UPDATE survey_invite SET existing_mode = 'resend'")
    util.remove_field(cr, "survey.invite", "public")
    util.remove_field(cr, "survey.invite", "public_url_html")
