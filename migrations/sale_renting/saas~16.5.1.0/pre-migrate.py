from odoo.upgrade import util


def migrate(cr, version):
    util.remove_model(cr, "rental.wizard")
    util.remove_field(cr, "rental.order.wizard.line", "is_late")
    util.remove_field(cr, "rental.order.wizard", "has_late_lines")
    util.remove_field(cr, "sale.order", "has_late_lines")
    util.remove_field(cr, "sale.order.line", "is_late")
    util.remove_constraint(cr, "sale_order_line", "sale_order_line_rental_period_coherence")
    util.remove_column(cr, "sale_order_line", "start_date")
    util.remove_column(cr, "sale_order_line", "return_date")
    util.remove_column(cr, "sale_order", "has_pickable_lines")
    util.remove_column(cr, "sale_order", "has_returnable_lines")
