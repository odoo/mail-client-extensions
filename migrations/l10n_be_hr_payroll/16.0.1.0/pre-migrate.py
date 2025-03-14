from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "hr.contract", "time_credit_full_time_wage")
    util.remove_field(cr, "hr.contract.history", "time_credit_full_time_wage")

    util.remove_view(cr, "l10n_be_hr_payroll.contract_employee_report_view_dashboard_inherit")
