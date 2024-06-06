from odoo.upgrade import util


def migrate(cr, version):
    util.rename_xmlid(cr, "data_cleaning.merge_action_project_task", "data_merge_project.merge_action_project_task")
    util.rename_xmlid(cr, "data_cleaning.merge_action_project_tags", "data_merge_project.merge_action_project_tags")
