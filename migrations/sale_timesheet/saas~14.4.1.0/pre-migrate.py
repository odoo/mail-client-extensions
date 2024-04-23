from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "project.create.sale.order", "link_selection")
    util.remove_field(cr, "project.create.sale.order", "pricing_type")
    util.remove_field(cr, "project.create.sale.order.line", "sale_line_id")
    util.remove_constraint(cr, "project_project", "project_project_sale_order_required_if_sale_line")
    util.remove_column(cr, "project_project", "pricing_type")  # This field will be a compute non-stored field
