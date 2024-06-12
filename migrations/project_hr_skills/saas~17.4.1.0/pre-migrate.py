from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "project_hr_skills.project_sharing_project_task_view_search")
