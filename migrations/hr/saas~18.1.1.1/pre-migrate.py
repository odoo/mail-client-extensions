from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "hr.hr_employee_comp_rule")
    util.remove_record(cr, "hr.hr_employee_public_comp_rule")
    util.remove_field(cr, "hr.departure.wizard", "employee_id")
    util.remove_column(cr, "hr_job", "expected_employees")
    util.remove_column(cr, "hr_job", "no_of_employee")
