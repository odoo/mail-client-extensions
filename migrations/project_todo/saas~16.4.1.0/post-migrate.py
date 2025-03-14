from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "project_todo.task_visibility_rule_project_user", util.update_record_from_xml)
