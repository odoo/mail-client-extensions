from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "sale_project.sale_project_milestone_view_tree")
    util.rename_field(cr, "project.milestone", "product_uom", "product_uom_id")
