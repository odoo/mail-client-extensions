from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_field(cr, "project.project", "budget")
    util.remove_field(cr, "project.project", "total_practical_amount")
    util.rename_field(cr, "project.project", "total_planned_amount", "total_budget_amount")

    util.remove_view(cr, "project_account_budget.crossovered_budget_lines_view_tree_inherit")
    util.rename_xmlid(
        cr,
        "project_account_budget.crossovered_budget_view_form_dialog",
        "project_account_budget.view_budget_analytic_form_dialog",
    )
