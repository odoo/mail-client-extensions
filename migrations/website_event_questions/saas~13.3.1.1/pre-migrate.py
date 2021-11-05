# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    # 1. remove reporting
    util.remove_model(cr, "event.question.report")
    util.remove_menus(cr, [util.ref(cr, "website_event_questions.menu_report_event_questions")])

    # 2. adapt current models to new event question models
    util.create_column(cr, "event_question", "question_type", "varchar", default="simple_choice")
    util.rename_field(cr, "event.question", "is_individual", "once_per_order")
    cr.execute("UPDATE event_question SET once_per_order = NOT once_per_order")

    util.rename_model(cr, "event.answer", "event.question.answer")

    # 3. remove direct m2m answer_ids on registration and modify event.registration.answer
    # event_registration_answer was a modeled m2m table but is now a fully independent model

    # 3a. add new columns
    util.rename_field(cr, "event.registration.answer", "event_answer_id", "value_answer_id")
    util.rename_field(cr, "event.registration.answer", "event_registration_id", "registration_id")
    util.create_column(cr, "event_registration_answer", "question_id", "int4")
    util.create_column(cr, "event_registration_answer", "value_text_box", "varchar")

    # 3b. populate new columns based on old columns values
    cr.execute(
        """
        UPDATE event_registration_answer ra
           SET question_id = qa.question_id
          FROM event_question_answer qa
         WHERE qa.id = ra.value_answer_id
        """
    )

    # 3c. remove old columns and direct m2m from registration to answer
    util.remove_field(cr, "event.registration", "answer_ids", drop_column=False)

    # 4. remove useless search view and rename some other views according to guidelines
    util.remove_view(cr, "website_event_questions.view_registration_search_inherit_question")
    eb = util.expand_braces

    renames = """
        {view_event,event_event_view}_form_inherit_question

        event{,_question}_answer_all
        event{,_question}_answer_event_user
    """

    for rename in util.splitlines(renames):
        util.rename_xmlid(cr, *eb(f"website_event_questions.{rename}"), noupdate=False)

    util.remove_record(cr, "website_event_questions.event_registration_answer_all")

    gone_views = """
        view_event_question_form
        view_event_answer_simplified_form
        view_event_registration_form_inherit_question
        view_registration_search_inherit_question
    """
    for view in util.splitlines(gone_views):
        util.remove_view(cr, f"website_event_questions.{view}")
