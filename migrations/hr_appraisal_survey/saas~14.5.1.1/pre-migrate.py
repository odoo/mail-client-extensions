# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):

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
