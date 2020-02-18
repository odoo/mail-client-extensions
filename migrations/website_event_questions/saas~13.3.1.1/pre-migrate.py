# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.upgrade import util


def migrate(cr, version):
    # 1. remove reporting
    util.remove_model(cr, "event.question.report")
    util.remove_menus(cr, [util.ref(cr, "website_event_questions.menu_report_event_questions")])

    # 2. adapt current models to new event question models
    util.create_column(cr, "event_question", "question_type", "varchar")
    cr.execute("UPDATE event_question SET question_type = 'simple_choice'")
    util.rename_model(cr, "event.answer", "event.question.answer")

    # 3. remove direct m2m answer_ids on registration and modify event.registration.answer
    # event_registration_answer was a modeled m2m table but is now a fully independent model

    # 3a. add new columns
    util.create_column(cr, "event_registration_answer", "question_id", "int4")
    util.create_column(cr, "event_registration_answer", "registration_id", "int4")
    util.create_column(cr, "event_registration_answer", "value_answer_id", "int4")
    util.create_column(cr, "event_registration_answer", "value_text_box", "varchar")

    # 3b. populate new columns based on old columns values
    cr.execute("""
        UPDATE event_registration_answer
           SET question_id = event_question_answer.question_id,
               registration_id = event_registration_id,
               value_answer_id = event_answer_id
          FROM event_question_answer
         WHERE event_question_answer.id = event_registration_answer.event_answer_id
    """)

    # 3c. remove old columns and direct m2m from registration to answer
    util.remove_field(cr, "event.registration.answer", "event_answer_id")
    util.remove_field(cr, "event.registration.answer", "event_registration_id")
    util.remove_field(cr, "event.registration", "answer_ids")

    # 4. remove useless search view and rename some other views according to guidelines
    util.remove_view(cr, "website_event_questions.view_registration_search_inherit_question")
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("website_event_questions.{view_event_question,event_question_view}_form"))
    util.rename_xmlid(cr, *eb("website_event_questions.{view_event,event_event_view}_form_inherit_question"))
    util.rename_xmlid(cr, *eb("website_event_questions.{view_event_registration,event_registration_view}_form_inherit_question"))
