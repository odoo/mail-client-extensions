from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "hr_appraisal_survey.mail_template_appraisal_ask_feedback", util.update_record_from_xml)
