from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "project_todo.todo_user_onboarding", util.update_record_from_xml)
