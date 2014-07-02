# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    if util.table_exists(cr, 'survey'):
        # clean hr_evaluation stuff
        cr.execute("delete from hr_evaluation_evaluation")
        cr.execute("delete from hr_evaluation_plan")
        return

    # Set hr_evaluation_interview 'state' and 'user_id'
    cr.execute("""update hr_evaluation_interview ei
                set state = sr.state, user_id = sr.user_id
                from survey_request sr
                where sr.id=ei.request_id""")

    # Set hr_evaluation_interview 'phase_id'
    cr.execute("""update hr_evaluation_interview ei
                set phase_id = epp.id
                from hr_evaluation_plan_phase epp,
                survey_user_input ui, hr_evaluation_evaluation ee, survey_request sr
                where epp.survey_id = ui.survey_id and epp.plan_id = ee.plan_id and ei.evaluation_id = ee.id
                and sr.response = ui.old_response_id and sr.id=ei.request_id""")

    # Set survey_user_input deadline (which will be reflected in hr_evaluation_interview)
    # Only requests with responses will be able to receive a deadline
    cr.execute("""update survey_user_input ui
                set deadline = sr.date_deadline
                from survey_request sr, hr_evaluation_interview ei
                where sr.id=ei.request_id
                and sr.response = ui.old_response_id""")

    # request_id now references survey_user_input instead of survey_request
    cr.execute("""update hr_evaluation_interview ei
                set request_id = ui.id
                from survey_request sr, survey_user_input ui
                where sr.id=ei.request_id
                and sr.response = ui.old_response_id""")
