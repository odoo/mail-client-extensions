from odoo.upgrade import util


def migrate(cr, version):
    util.move_field_to_module(cr, "event.type", "question_ids", "website_event", "event")
    util.move_field_to_module(cr, "event.event", "question_ids", "website_event", "event")
    util.move_field_to_module(cr, "event.event", "general_question_ids", "website_event", "event")
    util.move_field_to_module(cr, "event.event", "specific_question_ids", "website_event", "event")
    util.move_field_to_module(cr, "event.registration", "registration_answer_ids", "website_event", "event")
    util.move_field_to_module(cr, "event.registration", "registration_answer_choice_ids", "website_event", "event")

    util.move_model(cr, "event.question", "website_event", "event")
    util.move_model(cr, "event.question.answer", "website_event", "event")
    util.move_model(cr, "event.registration.answer", "website_event", "event")

    eb = util.expand_braces
    # addons/event/views/event_question_views.xml
    util.rename_xmlid(cr, *eb("{website_event,event}.event_question_view_form"))
    # addons/event/views/event_registration_answer_views.xml
    util.rename_xmlid(cr, *eb("{website_event,event}.event_registration_answer_view_search"))
    util.rename_xmlid(cr, *eb("{website_event,event}.event_registration_answer_view_tree"))
    util.rename_xmlid(cr, *eb("{website_event,event}.event_registration_answer_view_graph"))
    util.rename_xmlid(cr, *eb("{website_event,event}.event_registration_answer_view_pivot"))
    util.rename_xmlid(cr, *eb("{website_event,event}.action_event_registration_report"))
    # addons/event/security/ir.model.access.csv
    util.rename_xmlid(cr, *eb("{website_event,event}.access_event_question_user"))
    util.rename_xmlid(cr, *eb("{website_event,event}.access_event_question_answer_employee"))
    util.rename_xmlid(cr, *eb("{website_event,event}.access_event_question_answer_registration"))
    util.rename_xmlid(cr, *eb("{website_event,event}.access_event_question_answer_user"))
    util.rename_xmlid(cr, *eb("{website_event,event}.access_event_registration_answer"))

    if util.module_installed(cr, "whatsapp_event"):
        util.move_field_to_module(cr, "event.registration", "date_range", "whatsapp_event", "event")
        util.rename_field(cr, "event.registration", "date_range", "event_date_range")
