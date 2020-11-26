# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "project.mail_channel_project_task", util.remove_record)

    util.create_column(cr, "project_task", "display_project_id", "int4")
    # compute field
    # here we set the display_project_id for all the previous tasks, including subtasks to do not change
    # behaviour in various views for historic data's.
    query = "UPDATE project_task SET display_project_id = project_id"
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="project_task"))

    util.remove_field(cr, "project.task", "subtask_project_id")
    util.remove_field(cr, "project.project", "subtask_project_id")
