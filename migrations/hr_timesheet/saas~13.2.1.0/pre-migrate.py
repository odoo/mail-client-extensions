# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "hr_timesheet.web_tour_project_consumed_by_admin")

    pv = util.parse_version
    src_module = "timesheet_grid" if pv(version) >= pv("saas~13.1") else "sale_timesheet_enterprise"

    util.move_field_to_module(
        cr, "project.project", "allow_timesheet_timer", "sale_timesheet_enterprise", "hr_timesheet"
    )
    util.create_column(cr, "project_project", "allow_timesheet_timer", "boolean")
    cr.execute(
        """
        UPDATE project_project
           SET allow_timesheet_timer = allow_timesheets
         WHERE allow_timesheet_timer IS NULL
    """
    )

    for suffix in ["start", "pause"]:
        util.move_field_to_module(cr, "project.task", f"timesheet_timer_{suffix}", src_module, "hr_timesheet")
        util.remove_column(cr, "project_task", f"timesheet_timer_{suffix}")  # now related (to computed m2o)
        util.rename_field(cr, "project.task", f"timesheet_timer_{suffix}", f"timer_{suffix}")
        util.remove_field_metadata(cr, "project.task", f"timer_{suffix}")  # field part of mixin

    util.move_field_to_module(cr, "project.task", "timesheet_timer_first_start", src_module, "hr_timesheet")
    util.move_field_to_module(cr, "project.task", "timesheet_timer_last_stop", src_module, "hr_timesheet")
    util.move_field_to_module(cr, "project.task", "display_timesheet_timer", src_module, "hr_timesheet")
    util.create_column(cr, "project_task", "timesheet_timer_first_start", "timestamp")
    util.create_column(cr, "project_task", "timesheet_timer_last_stop", "timestamp")

    util.create_column(cr, "project_task", "overtime", "float8")
    cr.execute(
        """
            UPDATE project_task
               SET overtime = CASE WHEN planned_hours > 0
                                   THEN GREATEST(effective_hours + subtask_effective_hours - planned_hours, 0)
                                   ELSE 0
                               END
        """
    )

    util.move_field_to_module(cr, "res.config.settings", "timesheet_min_duration", src_module, "hr_timesheet")
    util.move_field_to_module(cr, "res.config.settings", "timesheet_rounding", src_module, "hr_timesheet")
    util.create_column(cr, "res_config_settings", "timesheet_min_duration", "integer")
    util.create_column(cr, "res_config_settings", "timesheet_rounding", "integer")

    util.move_model(cr, "project.task.create.timesheet", src_module, "hr_timesheet")

    # data
    eb = util.expand_braces
    renames = """
        project_view_form_inherit
        project_project_view_form_simplified_inherit
        project_task_view_form
        project_task_view_kanban
        project_task_create_timesheet_view_form
    """
    for xid in util.splitlines(renames):
        util.rename_xmlid(cr, *eb(f"{{{src_module},hr_timesheet}}.{xid}"))

    util.remove_view(cr, "hr_timesheet.view_task_form2_inherited_hr_timesheet")
