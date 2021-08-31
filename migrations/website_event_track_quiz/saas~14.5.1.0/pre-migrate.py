# -- coding: utf-8 --
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "event.quiz", "event_track_ids")
    util.remove_view(cr, "website_event_track_quiz.event_quiz_view_form_from_track")
    util.create_column(cr, "event_quiz", "repeatable", "boolean")
    util.create_column(cr, "event_quiz_answer", "is_correct", "boolean")
    cr.execute("UPDATE event_quiz_answer SET is_correct = (COALESCE(awarded_points, 0) > 0)")
