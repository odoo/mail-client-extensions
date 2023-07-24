from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "hr_recruitment.hr_employee_view_search")
    util.remove_record(cr, "hr_recruitment.hr_employee_action_from_department")
