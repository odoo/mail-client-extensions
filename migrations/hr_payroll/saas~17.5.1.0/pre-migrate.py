from odoo.upgrade import util


def migrate(cr, version):
    util.remove_model(cr, "hr.salary.attachment.report")
    util.remove_menus(cr, [util.ref(cr, "hr_payroll.menu_hr_payroll_attachment_salary_report")])
