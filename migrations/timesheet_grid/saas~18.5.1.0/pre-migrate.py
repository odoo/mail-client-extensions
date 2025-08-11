from odoo.upgrade import util


def migrate(cr, version):
    def is_timesheet_to_project_id_adapter(leaf, _or, _neg):
        left, op, right = leaf
        if op not in ["=", "!="]:
            return [leaf]
        if right:
            right = False
            op = "!=" if op == "=" else "="
        return [(left, op, right)]

    util.domains.adapt_domains(
        cr, "account.analytic.line", "is_timesheet", "project_id", adapter=is_timesheet_to_project_id_adapter
    )
    util.remove_field(cr, "account.analytic.line", "is_timesheet")
    util.domains.adapt_domains(
        cr, "timesheets.analytic.report", "is_timesheet", "project_id", adapter=is_timesheet_to_project_id_adapter
    )
    util.remove_field(cr, "timesheets.analysis.report", "is_timesheet")
    util.remove_field(cr, "res.users", "timesheet_manager_id")

    util.remove_view(cr, "timesheet_grid.res_users_view_form")
