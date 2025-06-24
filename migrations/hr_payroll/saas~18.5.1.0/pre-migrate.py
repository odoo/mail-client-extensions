from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "hr_payroll.menu_report_payroll")
    util.remove_field(cr, "hr.salary.rule", "appears_on_payroll_report")
    util.remove_model(cr, "hr.payroll.report")
