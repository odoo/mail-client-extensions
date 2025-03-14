from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "project.view_project_kanban_inherit")
