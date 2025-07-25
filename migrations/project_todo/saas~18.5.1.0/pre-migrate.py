from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "project_todo.project_task_preload_action_todo")
    util.remove_group(cr, "project_todo.group_onboarding_todo")
