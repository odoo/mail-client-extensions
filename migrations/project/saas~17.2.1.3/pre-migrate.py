from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "project.project", "closed_task_count")
    util.remove_field(cr, "project.share.wizard", "display_access_mode")
