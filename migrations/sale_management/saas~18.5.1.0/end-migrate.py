from odoo.upgrade import util


def migrate(cr, version):
    # Compute optional lines fields
    cr.execute("SELECT id FROM sale_order_line WHERE _upg_new_sol IS TRUE")
    optional_lines = [line[0] for line in cr.fetchall()]

    fields_to_compute = ["tax_ids"]
    if util.module_installed(cr, "sale_margin"):
        fields_to_compute.append("purchase_price")
    if util.module_installed(cr, "sale_management_renting"):
        fields_to_compute.append("is_rental")

    util.recompute_fields(cr, "sale.order.line", fields_to_compute, optional_lines, strategy="commit")
    util.remove_column(cr, "sale_order_line", "_upg_new_sol")
