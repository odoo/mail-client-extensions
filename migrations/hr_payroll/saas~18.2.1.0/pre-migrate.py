from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "hr_payroll.view_resource_calendar_search_inherit_payroll")
    util.remove_view(cr, "hr_payroll.resource_calendar_view_tree")
    util.remove_view(cr, "hr_payroll.payroll_resource_calendar_view_form")
