from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "project.act_res_users_2_project_task_opened")
