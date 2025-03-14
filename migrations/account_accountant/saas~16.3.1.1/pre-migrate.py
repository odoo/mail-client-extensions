from odoo.upgrade import util


def migrate(cr, version):
    util.force_noupdate(cr, "account_accountant.digest_tip_account_accountant_0", False)
    util.force_noupdate(cr, "account_accountant.digest_tip_account_accountant_1", False)
    util.remove_model(cr, "account.reconciliation.widget")
    util.remove_menus(cr, [util.ref(cr, "account_accountant.menu_action_manual_reconciliation")])
    util.remove_record(cr, "account_accountant.action_manual_reconciliation")
    util.remove_record(cr, "account_accountant.action_backport_reconcile_wizard")

    # Deferred management
    util.move_field_to_module(
        cr, "account.move.line", "subscription_start_date", "sale_subscription", "account_accountant"
    )
    util.move_field_to_module(
        cr, "account.move.line", "subscription_end_date", "sale_subscription", "account_accountant"
    )
    util.rename_field(cr, "account.move.line", "subscription_start_date", "deferred_start_date")
    util.rename_field(cr, "account.move.line", "subscription_end_date", "deferred_end_date")
    util.create_column(cr, "account_move_line", "deferred_start_date", "date")
    util.create_column(cr, "account_move_line", "deferred_end_date", "date")
    util.create_m2m(
        cr, "account_move_deferred_rel", "account_move", "account_move", "original_move_id", "deferred_move_id"
    )
