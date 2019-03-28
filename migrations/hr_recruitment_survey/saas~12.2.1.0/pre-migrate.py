# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute(
        """
        UPDATE survey_survey
           SET category = 'hr_recruitment',
               access_mode = 'token'
         WHERE id = %s
            OR id IN (SELECT survey_id FROM hr_job)
    """,
        [util.ref(cr, "hr_recruitment_survey.survey_recruitment_form")],
    )
