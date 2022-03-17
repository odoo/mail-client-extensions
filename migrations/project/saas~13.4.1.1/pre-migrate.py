# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "project_task_type", "active", "boolean", default=True)
    util.move_field_to_module(cr, "project.task.type", "is_closed", "project_enterprise", "project")
    util.create_column(cr, "project_task_type", "is_closed", "boolean", default=False)

    util.create_column(cr, "project_project", "description", "text")
    util.create_column(cr, "project_project", "rating_active", "boolean")
    util.create_column(cr, "project_project", "allow_subtasks", "boolean")
    util.remove_column(cr, "project_project", "resource_calendar_id")  # now related
    # NOTE: keep column as it is used to upgrade `website_project`
    util.remove_field(cr, "project.project", "portal_show_rating", drop_column=False)

    cr.execute(
        """
            UPDATE project_project
               SET allow_subtasks = EXISTS(SELECT 1
                                             FROM res_groups_implied_rel
                                            WHERE gid = %s
                                              AND hid = %s),
                   rating_active = rating_status != 'no',
                   rating_status = CASE WHEN rating_status = 'no' THEN 'stage' ELSE rating_status END

        """,
        [util.ref(cr, "base.group_user"), util.ref(cr, "project.group_subtask_project")],
    )
    cr.execute("UPDATE project_project SET rating_status_period = 'monthly' WHERE rating_status_period IS NULL")

    util.remove_field(cr, "project.task", "date_deadline_formatted")
    util.create_column(cr, "project_task", "partner_email", "varchar")
    util.create_column(cr, "project_task", "partner_phone", "varchar")
    util.parallel_execute(
        cr,
        util.explode_query_range(
            cr,
            """
                UPDATE project_task t
                   SET partner_email = p.email,
                       partner_phone = p.phone
                  FROM res_partner p
                 WHERE p.id = t.partner_id
            """,
            table="project_task",
            alias="t",
        ),
    )

    # data
    util.force_noupdate(cr, "project.rating_project_request_email_template", False)
    for filter_ in "task_pipe workload responsible cumulative_flow".split():
        util.remove_record(cr, f"project.filter_task_report_{filter_}")

    util.remove_record(cr, "project.access_mail_alias")
    util.remove_record(cr, "project.ir_actions_server_project_sample")

    util.update_record_from_xml(cr, "project.digest_tip_project_0")
