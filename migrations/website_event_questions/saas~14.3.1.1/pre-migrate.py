# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    # Clean the ACLs XMLID
    acl_name_changes = {
        "all": "event_question",
        "event_user": "event_question_user",
        "answer_all": "event_question_answer",
        "answer_event_user": "event_question_answer_user",
    }
    for old_name, new_name in acl_name_changes.items():
        util.rename_xmlid(
            cr, f"website_event_questions.event_question_{old_name}", f"website_event_questions.access_{new_name}"
        )

    # Remove ACLs
    util.remove_record(cr, "website_event_questions.access_event_registration_answer_user")
