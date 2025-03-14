from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "sale_timesheet_enterprise.timesheet_view_tree_inherit")
    util.remove_view(cr, "sale_timesheet_enterprise.timesheet_view_form_so_line_inherit")
    util.remove_view(cr, "sale_timesheet_enterprise.timesheet_view_grid_by_billing_rate")
    util.remove_field(cr, "account.analytic.line", "has_so_access")
