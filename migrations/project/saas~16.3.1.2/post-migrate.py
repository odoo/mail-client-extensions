from odoo.upgrade import util


def migrate(cr, version):
    util.remove_column(cr, "project_task", "display_project_id")
