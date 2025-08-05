from odoo.addons.base.maintenance.migrations.util.accounting import upgrade_analytic_distribution
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "hr_expense.view_hr_expense_sheet_dashboard_tree")

    if util.delete_unused(cr, "hr_expense.product_product_fixed_cost"):
        util.delete_unused(cr, "hr_expense.product_product_fixed_cost_product_template")

    if util.delete_unused(cr, "hr_expense.product_product_zero_cost"):
        util.delete_unused(cr, "hr_expense.product_product_zero_cost_product_template")

    util.remove_record(cr, "hr_expense.hr_expense_actions_my_unsubmitted")
    util.remove_record(cr, "hr_expense.action_hr_expense_sheet_all_to_submit")
    util.remove_record(cr, "hr_expense.action_hr_expense_sheet_all_to_approve")
    util.remove_record(cr, "hr_expense.action_hr_expense_sheet_all_to_post")
    util.remove_record(cr, "hr_expense.action_hr_expense_sheet_all_to_pay")

    util.remove_menus(
        cr,
        [
            util.ref(cr, "hr_expense.menu_hr_expense_my_expenses_to_submit"),
            util.ref(cr, "hr_expense.menu_hr_expense_sheet_all_to_submit"),
            util.ref(cr, "hr_expense.menu_hr_expense_sheet_all_to_approve"),
            util.ref(cr, "hr_expense.menu_hr_expense_sheet_all_to_post"),
            util.ref(cr, "hr_expense.menu_hr_expense_sheet_all_to_pay"),
            util.ref(cr, "hr_expense.menu_hr_expense_sheet_all"),
        ],
    )

    upgrade_analytic_distribution(cr, model="hr.expense")
