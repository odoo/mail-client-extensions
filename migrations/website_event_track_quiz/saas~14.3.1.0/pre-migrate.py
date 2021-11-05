# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    # Remove ACLs
    util.remove_record(cr, "website_event_track_quiz.event_quiz_access_event_manager")
    util.remove_record(cr, "website_event_track_quiz.event_quiz_question_access_event_manager")
    util.remove_record(cr, "website_event_track_quiz.event_quiz_answer_access_event_manager")
