# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    # column used in `end-` script
    util.remove_field(cr, "account.tax.report.line", "country_id", drop_column=False)

    util.rename_field(cr, "account.group", "code_prefix", "code_prefix_start")
    util.create_column(cr, "account_group", "code_prefix_end", "varchar")
    cr.execute("UPDATE account_group SET code_prefix_end = code_prefix_start")

    cr.execute("ALTER TABLE account_journal_type_rel RENAME TO journal_account_type_control_rel")
    cr.execute("ALTER TABLE account_account_type_rel RENAME TO journal_account_control_rel")

    # bank statement
    util.create_column(cr, "account_bank_statement", "previous_statement_id", "int4")
    cr.execute(
        """
        WITH bnk_stmt AS (
            SELECT id, LAG(id) OVER(PARTITION BY journal_id ORDER BY date, id) as previous
              FROM account_bank_statement
        )
        UPDATE account_bank_statement s
           SET previous_statement_id = b.previous
          FROM bnk_stmt b
         WHERE b.id = s.id
    """
    )

    util.rename_field(cr, "account.cash.rounding", "account_id", "profit_account_id")
    util.create_column(cr, "account_cash_rounding", "loss_account_id", "int4")
    # field from `pos_cash_rounding` which has been merged into `point_of_sale`
    util.move_field_to_module(cr, "account.cash.rounding", "loss_account_id", "point_of_sale", "account")

    util.remove_field(cr, "account.account.template", "group_id")
    util.remove_field(cr, "account.account.template", "root_id")

    if util.module_installed(cr, "account_accountant"):
        util.move_model(cr, "account.reconciliation.widget", "account", "account_accountant", move_data=True)
    else:
        util.remove_model(cr, "account.reconciliation.widget")

    util.remove_model(cr, "report.account.report_agedpartnerbalance")

    # It's a m2o converted to a m2m.
    # But as it is a TransientModel, we can simply ignore existing data.
    # (We let the ORM create the m2m table)
    util.remove_field(cr, "account.move.reversal", "move_id")

    util.remove_field(cr, "tax.adjustments.wizard", "country_id")

    # data
    views = util.splitlines(
        """
        account_tax_report_line_search
        view_account_bank_journal_tree
        account_bank_journal_view_kanban
        view_account_bank_journal_form

        report_agedpartnerbalance
    """
    )
    for view in views:
        util.remove_view(cr, f"account.{view}")

    records = util.splitlines(
        """
        action_view_account_move_line_reconcile
        action_manual_reconcile
        action_account_bank_journal_form
        action_bank_reconcile
        action_manual_reconciliation

    """
    )
    for record in records:
        util.remove_record(cr, f"account.{record}")

    util.remove_menus(
        cr,
        [
            util.ref(cr, "account.menu_action_account_invoice_bank_journal_form"),
            util.ref(cr, "account.menu_action_manual_reconciliation"),
        ],
    )

    util.force_noupdate(cr, "account.action_configure_tax_report")
    cr.execute(
        "UPDATE ir_act_window SET context='{}' WHERE id=%s", [util.ref(cr, "account.action_configure_tax_report")]
    )
