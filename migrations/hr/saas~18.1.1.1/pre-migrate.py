from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "hr.hr_employee_comp_rule")
    util.remove_record(cr, "hr.hr_employee_public_comp_rule")
