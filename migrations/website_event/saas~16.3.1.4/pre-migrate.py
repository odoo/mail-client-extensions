# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "website_event.res_config_settings_view_form")
    util.remove_view(cr, "website_event.registration_attendee_details_questions")
    util.remove_view(cr, "website_event.event_registration_view_form_inherit_question")
    util.remove_view(cr, "website_event.event_type_view_form_inherit_question")
