from odoo.upgrade import util


def migrate(cr, version):
    util.force_noupdate(cr, "project.group_project_rating", noupdate=False)
    util.remove_record(cr, "project.act_res_users_2_project_task_opened")
    util.remove_field(cr, "project.share.wizard", "access_mode")
    util.remove_field(cr, "project.share.wizard", "send_email")
    util.remove_view(cr, "project.project_sharing_access_view_tree")
    util.remove_view(cr, "project.project_collaborator_view_search")
    util.remove_record(cr, "project.project_collaborator_action")
