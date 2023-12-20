from odoo.upgrade import util


def migrate(cr, version):
    util.force_noupdate(cr, "project.group_project_rating", noupdate=False)
    util.remove_record(cr, "project.act_res_users_2_project_task_opened")
