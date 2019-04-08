# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_model(cr, *eb("account.batch.{deposit,payment}"))
    util.create_column(cr, "account_batch_payment", "batch_type", "varchar")
    util.create_column(cr, "account_batch_payment", "payment_method_id", "int4")
    util.create_column(cr, "account_batch_payment", "export_file_create_date", "date")
    cr.execute(
        "UPDATE account_batch_payment SET batch_type='inbound', payment_method_id=%s",
        [util.ref(cr, "account_batch_payment.account_payment_method_batch_deposit")],
    )

    util.rename_field(cr, "account.payment", *eb("batch_{deposit,payment}_id"))

    cr.execute("UPDATE account_payment_method SET code='batch_payment' WHERE code='batch_deposit'")

    util.remove_field(cr, "account.journal", "batch_deposit_sequence_id")
    util.remove_field(cr, "account.journal", "batch_deposit_payment_method_selected")

    util.rename_model(
        cr,
        "report.account_batch_deposit.print_batch_deposit",
        "report.account_batch_payment.print_batch_payment",
        rename_table=False,
    )

    renames = util.splitlines(
        """
        print_batch_{}
        action_print_batch_{}
        account_batch_{}_comp_rule
        access_account_batch_{}
        action_account_print_batch_{}
        action_account_create_batch_{}
        view_batch_{}_form
        view_batch_{}_search
        view_batch_{}_tree
    """
    )
    for r in renames:
        util.rename_xmlid(cr, *eb("account_batch_payment." + r.format("{deposit,payment}")), False)

    util.remove_record(cr, "account_batch_payment.action_batch_deposit")
    util.remove_record(cr, "account_batch_payment.menu_batch_deposit")
    util.remove_view(cr, "account_batch_payment.view_account_journal_form_inherited")
    util.remove_view(cr, "account_batch_payment.view_account_bank_journal_form_inherited_batch_deposit")
