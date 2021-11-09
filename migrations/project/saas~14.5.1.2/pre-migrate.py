# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.create_m2m(cr, "project_project_project_tags_rel", "project_project", "project_tags")
    util.create_column(cr, "project_project", "stage_id", "int4")

    # Create m2m with intermediate model `project.task.personal.stage`
    # Let the orm take care of foreign keys and other rules
    cr.execute(
        """
        CREATE TABLE project_task_user_rel (
            id          SERIAL NOT NULL PRIMARY KEY,
            create_uid  integer,
            create_date timestamp without time zone,
            write_uid   integer,
            write_date  timestamp without time zone,

            task_id     integer NOT NULL,
            user_id     integer NOT NULL,
            stage_id    integer
        )
    """
    )
    # Create our 6 default stage for every user having the group `group_project_user`
    # Fetch the appropriate users
    util.create_column(cr, "project_task_type", "user_id", "int4")
    cr.execute(
        """
        WITH stages AS (
           SELECT *
             FROM (VALUES (1, 'Inbox', false),
                                        (2, 'Today', false),
                                        (3, 'This Week', false),
                                        (4, 'This Month', false),
                                        (5, 'Later', false),
                                        (6, 'Done', true),
                                        (7, 'Canceled', true)
             ) x(seq, name, fold)
        ),
        assigned_users AS (
            SELECT DISTINCT user_id
              FROM project_task
             WHERE user_id IS NOT NULL
        )
        INSERT INTO
            project_task_type(
                sequence,
                name,
                user_id,
                fold,
                legend_blocked,
                legend_done,
                legend_normal,
                active
            )
            SELECT s.seq, s.name, a.user_id, s.fold,
                   'Blocked', 'Ready', 'In Progress', TRUE
              FROM assigned_users a,
                   stages s
        """
    )
    # Populate our new triplet with the data we need,
    # We migrate our assigned users and also assign their default stage.
    cr.execute(
        """
        INSERT INTO project_task_user_rel(task_id, user_id, stage_id)
             SELECT task.id, task.user_id, stage.id
               FROM project_task task
               JOIN project_task_type stage USING (user_id)
              WHERE stage.sequence = 1
                AND task.user_id IS NOT NULL
        """
    )
    util.update_field_references(cr, "user_id", "user_ids", only_models=("project.task",))

    # adapt email template (basic) expression
    for f in ["email_from", "email_to", "email_cc", "reply_to", "lang"]:
        cr.execute(
            fr"""
            UPDATE mail_template
                SET email_from = {f} = regexp_replace({f}, '\yobject\.user_id\y', 'object.user_ids[:1]', 'g')
              WHERE {f} ~ '\yobject\.user_id\y'
                AND model_id =
                    (SELECT id
                       FROM ir_model
                      WHERE model = 'project.task')
            """
        )

    util.remove_field(cr, "project.task", "user_id")
    util.remove_field(cr, "project.task", "user_email")
    util.update_record_from_xml(cr, "project.task_visibility_rule")

    cr.execute(
        """
            ALTER TABLE project_task
           ALTER COLUMN "working_hours_open" TYPE numeric,
           ALTER COLUMN "working_hours_close" TYPE numeric,
             ADD COLUMN "analytic_account_id" int4
        """
    )

    util.create_m2m(
        cr,
        "account_analytic_tag_project_task_rel",
        "account_analytic_tag",
        "project_task",
        "account_analytic_tag_id",
        "project_task_id",
    )
    util.rename_field(cr, "report.project.task.user", "user_id", "user_ids")
    util.rename_field(cr, "project.task.burndown.chart.report", "user_id", "user_ids")
