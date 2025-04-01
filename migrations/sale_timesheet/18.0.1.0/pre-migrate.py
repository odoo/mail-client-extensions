from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "sale_timesheet.project_sharing_inherit_project_task_view_tree_sale_timesheet")
