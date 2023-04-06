# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    if not util.module_installed(cr, 'project_timesheet'):
        util.delete_model(cr, 'project.task.work')
    util.delete_model(cr, 'project.task.delegate')
    cr.execute("DROP VIEW IF EXISTS report_project_task_user")

    # projects
    cr.execute("""UPDATE project_project
                     SET privacy_visibility='portal'
                   WHERE privacy_visibility='public'
               """)
    cr.execute("UPDATE project_project SET state='cancelled' WHERE state='template'")
    util.create_column(cr, 'project_project', 'user_id', 'int4')
    cr.execute("""
        UPDATE project_project
        SET user_id = a.user_id
        FROM account_analytic_account a
        WHERE analytic_account_id = a.id""")

    for c in 'planned_hours effective_hours total_hours progress_rate'.split():
        util.remove_field(cr, 'project.project', c)

    cr.execute("DROP TABLE project_user_rel")   # old m2m

    # link default stages
    cr.execute("""
        INSERT INTO project_task_type_rel(type_id, project_id)
        SELECT t.id, p.id
          FROM project_task_type t, project_project p
         WHERE t.case_default = true
           AND NOT EXISTS(SELECT 1 FROM project_task_type_rel WHERE type_id=t.id AND project_id=p.id)
    """)

    # tasks
    cr.execute("UPDATE project_task SET kanban_state='normal' WHERE kanban_state IS NULL")
    for c in 'effective_hours total_hours delay_hours progress'.split():
        util.remove_field(cr, 'project.task', c)

    # categories/tags
    util.rename_model(cr, 'project.category', 'project.tags')
    cr.execute("""ALTER TABLE project_category_project_task_rel
                    RENAME TO project_tags_project_task_rel""")
    cr.execute("""ALTER TABLE project_tags_project_task_rel
                RENAME COLUMN project_category_id TO project_tags_id""")
    util.update_field_usage(cr, 'project.project', 'categ_ids', 'tag_ids')
    util.update_field_usage(cr, 'project.task', 'categ_ids', 'tag_ids')

    # force recreate columns of config wizard
    cr.execute("DROP TABLE project_config_settings")
    util.remove_view(cr, 'project.view_config_settings')

    # rename/keep some data
    for i in range(4):
        util.rename_xmlid(cr, 'project.project_category_0%d' % (i + 1,),
                          'project.project_tags_0%d' % i)
        util.force_noupdate(cr, 'project.project_stage_%d' % i, True)
    util.force_noupdate(cr, 'project.view_project_project_filter', False)
    util.force_noupdate(cr, 'project.all_projects_account', True)

    # cleanup filters
    cr.execute("""
        DELETE FROM ir_filters
              WHERE domain ~ '\ymembers\y'
                AND model_id IN ('project.project', 'project.task', 'project.issue')
    """)
