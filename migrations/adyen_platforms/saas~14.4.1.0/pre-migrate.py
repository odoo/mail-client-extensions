# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_model(cr, "adyen.payout")

    cr.execute("DELETE FROM adyen_transaction")
    cr.execute("DELETE FROM adyen_shareholder")
    cr.execute("DELETE FROM adyen_bank_account")
    cr.execute("DELETE FROM adyen_account")

    # adyen.account
    util.remove_field(cr, "adyen.account", "kyc_status")
    util.remove_field(cr, "adyen.account", "payout_ids")

    util.remove_column(cr, "adyen_account", "kyc_status_message")

    util.create_column(cr, "adyen_account", "account_code", "varchar")
    util.create_column(cr, "adyen_account", "payout_schedule", "varchar", default="biweekly")
    util.create_column(cr, "adyen_account", "next_scheduled_payout", "timestamp without time zone")
    util.create_column(cr, "adyen_account", "last_sync_date", "timestamp without time zone")
    util.create_column(cr, "adyen_account", "account_status", "varchar")
    util.create_column(cr, "adyen_account", "payout_allowed", "bool")
    util.create_column(cr, "adyen_account", "kyc_tier", "int4")

    # adyen.transaction
    util.remove_field(cr, "adyen.transaction", "adyen_payout_id")

    util.rename_field(cr, "adyen.transaction", "amount", "total_amount")

    util.remove_column(cr, "adyen_transaction", "status")

    util.create_column(cr, "adyen_transaction", "capture_reference", "varchar")
    util.create_column(cr, "adyen_transaction", "merchant_amount", "float8")
    util.create_column(cr, "adyen_transaction", "fees", "float8")
    util.create_column(cr, "adyen_transaction", "fixed_fees", "float8")
    util.create_column(cr, "adyen_transaction", "variable_fees", "float8")
    util.create_column(cr, "adyen_transaction", "fees_currency_id", "int4")
    util.create_column(cr, "adyen_transaction", "signature", "varchar")
    util.create_column(cr, "adyen_transaction", "reason", "varchar")
    util.create_column(cr, "adyen_transaction", "payment_method", "varchar")
    util.create_column(cr, "adyen_transaction", "shopper_country_id", "int4")
    util.create_column(cr, "adyen_transaction", "dispute_reference", "varchar")

    # adyen.shareholder
    util.remove_field(cr, "adyen.shareholder", "kyc_status")
    util.remove_field(cr, "adyen.shareholder", "kyc_status_message")
