from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "hr.leave", "manager_id")
    util.remove_view(cr, "hr_holidays.hr_employee_public_form_view_inherit")
