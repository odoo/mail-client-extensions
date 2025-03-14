from odoo.upgrade import util


def migrate(cr, version):
    cr.execute("UPDATE survey_survey SET survey_type = 'appraisal' WHERE is_appraisal")
    util.remove_field(cr, "survey.survey", "is_appraisal")
