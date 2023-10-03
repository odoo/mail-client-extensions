# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    good = util.ref(cr, "hr_appraisal_survey.mail_template_appraisal_ask_feedback_formatted")
    if good:
        bad = util.ref(cr, "hr_appraisal_survey.mail_template_appraisal_ask_feedback")
        if bad:
            util.replace_record_references_batch(cr, {bad: good}, "mail.template", replace_xmlid=False)
            util.remove_record(cr, "hr_appraisal_survey.mail_template_appraisal_ask_feedback")
        util.rename_xmlid(cr, *eb("hr_appraisal_survey.mail_template_appraisal_ask_feedback{_formatted,}"))
    else:
        util.update_record_from_xml(cr, "hr_appraisal_survey.mail_template_appraisal_ask_feedback")
    util.remove_field(cr, "appraisal.ask.feedback", "user_body")
    util.remove_view(cr, "hr_appraisal_survey.survey_user_input_view_tree")
