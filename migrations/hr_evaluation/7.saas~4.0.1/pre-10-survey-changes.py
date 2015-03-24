# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    if util.table_exists(cr, 'survey'):
        # clean hr_evaluation stuff
        cr.execute("delete from hr_evaluation_evaluation")
        cr.execute("delete from hr_evaluation_plan")
        return

    #1. Set hr_evaluation_interview 'state' and 'user_id'.
    util.create_column(cr, 'hr_evaluation_interview', 'state', 'varchar')
    util.create_column(cr, 'hr_evaluation_interview', 'user_id', 'int')
    cr.execute("""update hr_evaluation_interview ei
                set state = sr.state, user_id = sr.user_id
                from survey_request sr
                where sr.id=ei.request_id""")

    #2. Set survey_user_input 'deadline' (which will be reflected in hr_evaluation_interview).
    # Here, only requests with responses receive a deadline.
    cr.execute("""update survey_user_input ui
                set deadline = sr.date_deadline
                from survey_request sr, hr_evaluation_interview ei
                where sr.id=ei.request_id
                and sr.response = ui.old_response_id""")

    #3. request_id now references survey_user_input instead of survey_request.
    # So for each hr_evaluation_interview, a survey_user_user_input is needed (request_id has ondelete=cascade).
    # For each evaluation interview that has no response, create a new not-yet-started survey_user_input.

    # temp fields: to copy from and to be removed
    util.create_column(cr, 'hr_evaluation_interview', 'new_request_id', 'int')
    util.create_column(cr, 'hr_evaluation_interview', 'old_request_id', 'int')
    # save original request_id
    cr.execute("""update hr_evaluation_interview
                set old_request_id = request_id""")
    util.create_column(cr, 'survey_user_input', 'old_request_id', 'int')

    # To avoid losing hr_evaluation_interview records caused due to changes in structure.
    cr.execute("""ALTER TABLE hr_evaluation_interview
                DROP CONSTRAINT hr_evaluation_interview_request_id_fkey""")

    cr.execute("""select s.create_uid, s.create_date, s.write_date, s.date_deadline,
                s.write_uid, u.partner_id, s.survey_id, s.email, s.id
                from survey_request s left outer join res_users u
                on s.user_id = u.id
                where s.response is null""")
    new_inputs = cr.dictfetchall()
    import uuid
    for input in new_inputs:
        token = str(uuid.uuid4())
        cr.execute("""insert into survey_user_input(create_uid, create_date, date_create, deadline, write_date, write_uid,
                                                    partner_id, survey_id, email, old_request_id, state, type, token)
                    values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    [input['create_uid'], input['create_date'], input['create_date'], input['date_deadline'],
                     input['write_date'], input['write_uid'], input['partner_id'], input['survey_id'],
                     input['email'], input['id'], 'new', 'link', token, ])

    #3.1 update temp request_id of hr_evaluation_interviews without actual responses (referencing 'new' survey_user_inputs)
    cr.execute("""update hr_evaluation_interview ei
                set new_request_id = ui.id
                from survey_request sr, survey_user_input ui
                where sr.id=ei.request_id
                and sr.id = ui.old_request_id""")

    #3.2 update temp request_id of hr_evaluation_interviews having responses
    cr.execute("""update hr_evaluation_interview ei
                set new_request_id = ui.id
                from survey_request sr, survey_user_input ui
                where sr.id=ei.request_id
                and sr.response = ui.old_response_id""")

    # temp fields: copy and discard
    cr.execute("""update hr_evaluation_interview
                set request_id = new_request_id""")
    util.remove_column(cr, 'hr_evaluation_interview', 'new_request_id')
    util.remove_column(cr, 'hr_evaluation_interview', 'old_request_id')
    util.remove_column(cr, 'survey_user_input', 'old_request_id')


    #4. Set hr_evaluation_interview 'phase_id'.
    # Note: Manually entered hr_evaluation_interviews
    # (i.e. not based on an evaluation plan) will not have a phase_id.
    util.create_column(cr, 'hr_evaluation_interview', 'phase_id', 'int')
    intv_phs_map = []
    cr.execute("select distinct evaluation_id from hr_evaluation_interview")
    evaluations = cr.fetchall()

    for each_eval in evaluations:
        cr.execute("""select ei.id from hr_evaluation_interview ei, survey_user_input ui
                where ei.request_id = ui.id and evaluation_id = %s
                order by ei.id""", [each_eval, ])
        all_intvs = [m[0] for m in cr.fetchall()]

        cr.execute("""select epp.id from hr_evaluation_plan_phase epp
            where epp.plan_id in (select plan_id from hr_evaluation_evaluation where id = %s)
            order by epp.id""", [each_eval, ])
        all_phases = [m[0] for m in cr.fetchall()]

        intv_phs_map.extend(zip(all_intvs,all_phases))

    for intv, phase in intv_phs_map:
        cr.execute("update hr_evaluation_interview set phase_id = %s where id = %s", [phase, intv, ])
