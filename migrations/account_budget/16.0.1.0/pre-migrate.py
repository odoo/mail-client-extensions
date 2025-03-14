from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.rename_field(cr, "crossovered.budget.lines", "analytic_group_id", "analytic_plan_id")
