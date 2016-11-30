# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    cr.execute("""
        UPDATE hr_employee e
           SET appraisal_date=e.evaluation_date,
               appraisal_frequency=p.month_next,
               appraisal_frequency_unit='month',
               periodic_appraisal=true,
               appraisal_by_colleagues=false,
               appraisal_by_manager = EXISTS(SELECT 1
                                               FROM hr_evaluation_plan_phase
                                              WHERE plan_id=p.id
                                                AND action='top-down'),
               appraisal_manager_survey_id = (SELECT survey_id
                                                FROM hr_evaluation_plan_phase
                                               WHERE plan_id=p.id
                                                 AND action='top-down'
                                            ORDER BY sequence
                                               LIMIT 1),
               appraisal_self = EXISTS(SELECT 1
                                         FROM hr_evaluation_plan_phase
                                        WHERE plan_id=p.id
                                          AND action='self'),
               appraisal_by_collaborators = EXISTS(SELECT 1
                                                     FROM hr_evaluation_plan_phase
                                                    WHERE plan_id=p.id
                                                      AND action='bottom-up'),
               appraisal_collaborators_survey_id = (SELECT survey_id
                                                      FROM hr_evaluation_plan_phase
                                                     WHERE plan_id=p.id
                                                       AND action='bottom-up'
                                                  ORDER BY sequence
                                                     LIMIT 1)
          FROM hr_evaluation_plan p
         WHERE e.evaluation_plan_id = p.id
    """)
    cr.execute("""
        UPDATE hr_employee e
           SET appraisal_employee = r.name
          FROM resource_resource r
         WHERE r.id = e.resource_id
           AND e.appraisal_self
    """)
    cr.execute("""
        INSERT INTO emp_appraisal_manager_rel(hr_employee_id,hr_appraisal_id)
          SELECT id, parent_id
            FROM hr_employee
           WHERE appraisal_by_manager = true
             AND parent_id IS NOT NULL
    """)
    cr.execute("""
        INSERT INTO emp_appraisal_subordinates_rel(hr_employee_id, hr_appraisal_id)
          SELECT e.id, s.id
            FROM hr_employee e
            JOIN hr_employee s
              ON s.parent_id = e.id
           WHERE e.appraisal_by_collaborators = true
    """)

    util.create_column(cr, 'hr_appraisal', '_evid', 'int4')
    cr.execute("""
        WITH appr AS (
        INSERT INTO hr_appraisal(_evid, create_uid, create_date, write_uid, write_date,
                                 employee_id, date_close, action_plan, state)
            SELECT id, create_uid, create_date, write_uid, write_date, employee_id, coalesce(date_close, date),
                   note_action, CASE WHEN state='draft' THEN 'new'
                                     WHEN state in ('wait', 'progress') THEN 'pending'
                                     ELSE state
                                 END
              FROM hr_evaluation_evaluation
        RETURNING id, _evid
        ),
        userinput AS (
        UPDATE survey_user_input i
           SET appraisal_id=a.id
          FROM hr_evaluation_interview t, appr a
         WHERE a._evid = t.evaluation_id
           AND i.id = t.request_id
        RETURNING user_id, survey_id, appraisal_id
        ),

        _1 AS (
        UPDATE hr_appraisal a
           SET employee_appraisal=true, employee_survey_id=ui.survey_id
          FROM userinput ui, hr_evaluation_interview t, hr_employee e, resource_resource r
         WHERE ui.appraisal_id = a.id
           AND a._evid = t.request_id
           AND e.id = a.employee_id
           AND r.id = e.resource_id
           AND r.user_id = ui.user_id
        ),

        _2 AS (
        UPDATE hr_appraisal a
           SET manager_appraisal=true, manager_survey_id=ui.survey_id
          FROM userinput ui, hr_evaluation_interview t, hr_employee e, resource_resource r
         WHERE ui.appraisal_id = a.id
           AND a._evid = t.request_id
           AND e.id = (SELECT parent_id FROM hr_employee WHERE id=a.employee_id)
           AND r.id = e.resource_id
           AND r.user_id = ui.user_id
        ),
        _2l AS (
        INSERT INTO appraisal_manager_rel(hr_appraisal_id, hr_employee_id)
            SELECT a.id, e.parent_id
              FROM hr_appraisal a
              JOIN hr_employee e ON (a.employee_id = e.id)
             WHERE manager_appraisal = true
        ),

        _3 AS (
        UPDATE hr_appraisal a
           SET collaborators_appraisal=true, collaborators_survey_id=ui.survey_id
          FROM userinput ui, hr_evaluation_interview t, hr_employee e, resource_resource r
         WHERE ui.appraisal_id = a.id
           AND a._evid = t.request_id
           AND e.id = (SELECT id FROM hr_employee WHERE parent_id=a.employee_id)
           AND r.id = e.resource_id
           AND r.user_id = ui.user_id
        ),
        _3l AS (
        INSERT INTO appraisal_manager_rel(hr_appraisal_id, hr_employee_id)
            SELECT a.id, e.id
              FROM hr_appraisal a
              JOIN hr_employee e ON (a.employee_id = e.parent_id)
             WHERE collaborators_appraisal = true
        )
        SELECT 42
    """)

    cr.execute("SELECT _evid, id FROM hr_appraisal")
    for e, a in cr.fetchall():
        util.replace_record_references(cr, ('hr.evaluation.evaluation', e), ('hr.appraisal', a))

    # cleanup
    util.remove_column(cr, 'hr_appraisal', '_evid')
    util.delete_model(cr, 'hr_evaluation.plan')
    util.delete_model(cr, 'hr_evaluation.plan.phase')
    util.delete_model(cr, 'hr_evaluation.evaluation')
    util.delete_model(cr, 'hr_evaluation.interview')
