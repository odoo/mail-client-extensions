# -- coding: utf-8 --
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "event.quiz", "event_track_ids")
    util.remove_view(cr, "website_event_track_quiz.event_quiz_view_form_from_track")
