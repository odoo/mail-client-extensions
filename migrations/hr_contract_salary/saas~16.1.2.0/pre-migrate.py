from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "generate.simulation.link", "employee_contract_employee_id")
    util.remove_column(cr, "generate_simulation_link", "employee_id")
