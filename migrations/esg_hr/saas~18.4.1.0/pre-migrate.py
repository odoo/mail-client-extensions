from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "esg.employee.report", "gender", "sex")

    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("esg_hr.action_esg_employee_report_{gender,sex}_parity"))
    util.rename_xmlid(cr, *eb("esg_hr.menu_esg_{gender,sex}_parity"))
