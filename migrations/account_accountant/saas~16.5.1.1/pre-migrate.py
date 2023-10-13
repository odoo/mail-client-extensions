from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "account.reconcile.wizard", "transfer_amount")
    util.remove_field(cr, "account.reconcile.wizard", "transfer_amount_currency")

    # Deferred Management
    util.create_column(
        cr, "res_company", "generate_deferred_revenue_entries_method", "varchar", default="on_validation"
    )
    util.create_column(
        cr, "res_company", "generate_deferred_expense_entries_method", "varchar", default="on_validation"
    )
    if util.column_exists(cr, "res_company", "generate_deferred_entries_method"):
        cr.execute(
            """
            UPDATE res_company company
               SET generate_deferred_revenue_entries_method = generate_deferred_entries_method,
                   generate_deferred_expense_entries_method = generate_deferred_entries_method
            """
        )
    util.remove_field(cr, "res.config.settings", "generate_deferred_entries_method")
    util.remove_field(cr, "res.company", "generate_deferred_entries_method")

    util.remove_menus(cr, [util.ref(cr, "account_accountant.menu_action_auto_reconcile")])
