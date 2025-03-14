from odoo.upgrade import util


def migrate(cr, version):
    # removed view
    util.remove_view(cr, "hr_contract_reports.contract_employee_report_view_dashboard")
