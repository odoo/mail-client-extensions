# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces

    util.if_unchanged(cr, "hr_appraisal_survey.mail_template_appraisal_ask_feedback", util.update_record_from_xml)

    util.create_column(cr, "hr_department", "appraisal_survey_template_id", "integer")
    cr.execute(
        """
            UPDATE hr_department d
               SET appraisal_survey_template_id = c.appraisal_survey_template_id
              FROM res_company c
             WHERE c.id = d.company_id
        """
    )

    util.create_m2m(cr, "hr_appraisal_survey_survey_rel", "survey_survey", "hr_appraisal")
    cr.execute(
        """
        INSERT INTO hr_appraisal_survey_survey_rel(hr_appraisal_id, survey_survey_id)
             SELECT s.appraisal_id, s.survey_id
               FROM survey_user_input s
               JOIN hr_appraisal a ON a.id=s.appraisal_id
           GROUP BY s.appraisal_id, s.survey_id
        ON CONFLICT DO NOTHING
    """
    )

    util.rename_xmlid(cr, *eb("hr_appraisal_survey.survey_user_input_view_tree{_inherit_hr_appraisal,}"))
