from odoo.upgrade import util


def migrate(cr, version):
    util.update_record_from_xml(cr, "website_event.ir_rule_event_question_published")
    util.update_record_from_xml(cr, "website_event.ir_rule_event_question_answer_published")
