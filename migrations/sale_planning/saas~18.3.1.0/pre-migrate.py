from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "sale_planning.planning_role_view_kanban_inherit_sale_planning")
