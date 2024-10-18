from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "pos_hr.multi_employee_sales_report")
    util.remove_record(cr, "pos_hr.multi_employee_sales_report_action")
    util.remove_model(cr, "report.pos_hr.multi_employee_sales_report")
