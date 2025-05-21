from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "hr_appraisal_survey.res_config_settings_view_form_hr_appraisal_survey")
    util.remove_view(cr, "hr_appraisal_survey.hr_department_view_form")
    util.remove_field(cr, "res.config.settings", "appraisal_survey_template_id")
    util.remove_field(cr, "hr.department", "appraisal_survey_template_id")
    util.remove_field(cr, "res.company", "appraisal_survey_template_id")
