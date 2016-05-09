# -*- coding: utf-8 -*-
from operator import itemgetter
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'account_analytic_line', 'project_id', 'int4')

    cr.execute("""
        UPDATE account_analytic_line l
           SET project_id = p.id
          FROM project_project p
         WHERE p.analytic_account_id = l.account_id
           AND l.is_timesheet
    """)

    model_task = util.ref(cr, 'project.model_project_task')
    model_project = util.ref(cr, 'project.model_project_project')

    # create inactive private missing projects
    cr.execute("""
        WITH no_project AS (
            SELECT a.id, a.name
              FROM account_analytic_line l
              JOIN account_analytic_account a on (a.id = l.account_id)
             WHERE l.project_id IS NULL
               AND l.is_timesheet
          GROUP BY a.id
        ),
        _new_aliases AS (
            INSERT INTO mail_alias(alias_name, alias_contact, alias_defaults,
                                   alias_model_id, alias_parent_model_id, alias_parent_thread_id)
            SELECT 'project-' || regexp_replace(lower(name), '\W+', '-', 'g'), 'followers', '{}',
                   %s, %s, id
              FROM no_project
         RETURNING id, alias_parent_thread_id
        ),
        _new_projects AS (
            INSERT INTO project_project(analytic_account_id, alias_id, alias_model,
                                        privacy_visibility, label_tasks, state, active)
            SELECT a.alias_parent_thread_id, a.id, 'project.task', 'followers', 'Tasks', 'open', false
              FROM _new_aliases a
         RETURNING id
        ),
        _upd_aaa AS (
            UPDATE account_analytic_account a
               SET use_tasks = true
              FROM no_project n
             WHERE n.id = a.id
        ),
        _upd_aal AS (
            UPDATE account_analytic_line l
               SET project_id = p.id
              FROM project_project p
             WHERE p.analytic_account_id = l.account_id
               AND l.is_timesheet
               AND l.project_id IS NULL
        )
        SELECT id FROM _new_projects
    """, [model_task, model_project])

    new_project_ids = map(itemgetter(0), cr.fetchall())
    # weird limitation of CTE: we can't update records created in the same CTE query
    cr.execute("""
        UPDATE mail_alias a
           SET alias_parent_thread_id = p.id,
               alias_defaults = concat('{''project_id'': ', p.id, '}')
          FROM project_project p
         WHERE a.id = p.alias_id
           AND p.id = ANY(%s)
    """, [new_project_ids])
