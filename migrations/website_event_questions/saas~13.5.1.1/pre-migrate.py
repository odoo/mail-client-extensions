# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.rename_xmlid(
        cr,
        "website_event_questions.event_event_view_form_inherit_question",
        "website_event_questions.event_event_view_form",
    )
