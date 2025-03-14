from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "hr.hr_employee_action_from_user")
