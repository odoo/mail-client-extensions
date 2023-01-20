# -*- coding: utf-8 -*-
from odoo.upgrade import util
from odoo.upgrade.util import inconsistencies


def migrate(cr, version):
    fields_to_check = {
        "account.account": ["tax_ids"],
        "account.journal.group": ["excluded_journal_ids"],
        "account.journal": [
            "default_credit_account_id",
            "default_debit_account_id",
            "profit_account_id",
            "loss_account_id",
            "bank_account_id",
            "secure_sequence_id",
        ],
        "account.tax": ["children_tax_ids", "cash_basis_transition_account_id", "cash_basis_base_account_id"],
        "account.tax.repartition.line": ["account_id", "invoice_tax_id", "refund_tax_id"],
        "account.analytic.line": ["move_id"],
        "account.bank.statement": ["journal_id"],
        "account.bank.statement.line": ["account_id", "statement_id"],
        "account.move": [
            "journal_id",
            "reversed_entry_id",
            "fiscal_position_id",
            "invoice_payment_term_id",
            "invoice_partner_bank_id",
        ],
        "account.move.line": [
            "move_id",
            "journal_id",
            "account_id",
            "reconcile_model_id",
            "payment_id",
            "statement_line_id",
            "tax_ids",
            "tax_repartition_line_id",
            "analytic_account_id",
            "analytic_tag_ids",
        ],
        "account.payment": ["journal_id", "partner_bank_account_id", "invoice_ids"],
        "account.reconcile.model.line": [
            "account_id",
            "journal_id",
            "tax_ids",
            "analytic_account_id",
            "analytic_tag_ids",
        ],
        "account.reconcile.model": ["match_journal_ids"],
        "account.fiscal.position.tax": ["tax_src_id", "tax_dest_id"],
        "account.fiscal.position.account": ["account_src_id", "account_dest_id"],
    }
    if util.table_exists(cr, "account_account_type_rel"):
        fields_to_check["account.journal"].append("account_control_ids")

    if util.version_gte("saas~13.4"):
        # in saas~13.4, `account.payment` is now an _inherits on `account.move`
        fields_to_check["account.move.line"].remove("payment_id")
        del fields_to_check["account.payment"]

        # And some fields have been removed
        fields_to_check["account.tax"].remove("cash_basis_base_account_id")
        fields_to_check["account.bank.statement.line"].remove("account_id")
        # and renamed
        fields_to_check["account.move"].remove("invoice_partner_bank_id")
        fields_to_check["account.move"].append("partner_bank_id")

    if util.version_gte("saas~13.5"):
        fields_to_check["account.journal"].remove("default_credit_account_id")
        fields_to_check["account.journal"].remove("default_debit_account_id")
        fields_to_check["account.journal"].append("default_account_id")

    for model_name, field_names in fields_to_check.items():
        for field_name in field_names:
            inconsistencies.verify_companies(cr, model_name, field_name)
