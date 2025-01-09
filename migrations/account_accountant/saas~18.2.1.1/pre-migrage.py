from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "account_accountant.view_account_reconcile_model_widget_wizard")

    util.remove_menus(
        cr,
        [
            util.ref(cr, "account.menu_action_account_report_budget_tree"),
        ],
    )
