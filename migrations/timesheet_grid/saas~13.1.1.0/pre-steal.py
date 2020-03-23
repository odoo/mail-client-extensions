# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    if util.version_gte("saas~13.2"):
        # in saas~13.2, everything moves to `hr_timesheet`
        return

    eb = util.expand_braces

    moves = {
        "project.project": {"allow_timesheet_timer:boolean"},
        "project.task": {
            f"timesheet_timer_{suffix}:timestamp" for suffix in {"start", "pause", "first_start", "last_stop"}
        }
        | {"display_timesheet_timer"},
        "res.config.settings": {"timesheet_min_duration:integer", "timesheet_rounding:integer"},
    }

    util.move_field_to_module(
        cr, "project.project", "allow_timesheet_timer", "sale_timesheet_enterprise", "timesheet_grid"
    )
    for model, fields in moves.items():
        for field in fields:
            field, _, ftype = field.partition(":")

            util.move_field_to_module(cr, model, field, "sale_timesheet_enterprise", "timesheet_grid")
            if ftype:
                table = util.table_of_model(cr, model)
                util.create_column(cr, table, field, ftype)

    util.move_model(cr, "project.task.create.timesheet", "sale_timesheet_enterprise", "timesheet_grid")

    renames = util.splitlines(
        """
        # views
        project_task_view_kanban
        project_task_create_timesheet_view_form
    """
    )
    for xid in renames:
        util.rename_xmlid(cr, *eb(f"{{sale_timesheet_enterprise,timesheet_grid}}.{xid}"))
