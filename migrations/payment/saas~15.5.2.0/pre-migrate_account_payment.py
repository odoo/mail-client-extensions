from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces

    # Ir.ui.view
    util.rename_xmlid(cr, *eb("{payment,account_payment}.view_account_payment_register_form_inherit_payment"))
    util.rename_xmlid(cr, *eb("{payment,account_payment}.view_account_payment_form_inherit_payment"))
    util.rename_xmlid(cr, *eb("{payment,account_payment}.view_account_journal_form"))
    util.rename_xmlid(cr, *eb("{payment,account_payment}.account_invoice_view_form_inherit_payment"))
    util.rename_xmlid(cr, *eb("{payment,account_payment}.payment_refund_wizard_view_form"))

    # Ir.actions.act_window
    util.rename_xmlid(cr, *eb("{payment,account_payment}.action_invoice_order_generate_link"))

    # Ir.rule
    util.rename_xmlid(cr, *eb("{payment,account_payment}.payment_transaction_billing_rule"))
    util.rename_xmlid(cr, *eb("{payment,account_payment}.payment_token_billing_rule"))

    # Ir.ui.menu
    util.rename_xmlid(
        cr,
        "payment.payment_acquirer_menu",
        "account_payment.payment_provider_menu",
    )
    util.rename_xmlid(cr, *eb("{payment,account_payment}.payment_icon_menu"))
    util.rename_xmlid(cr, *eb("{payment,account_payment}.payment_token_menu"))
    util.rename_xmlid(cr, *eb("{payment,account_payment}.payment_transaction_menu"))

    util.move_model(cr, "payment.refund.wizard", "payment", "account_payment", move_data=True)

    moved_fields = {
        "account.move": ["transaction_ids", "authorized_transaction_ids", "amount_paid"],
        "account.payment": [
            "payment_transaction_id",
            "payment_token_id",
            "amount_available_for_refund",
            "suitable_payment_token_ids",
            "use_electronic_payment_method",
            "source_payment_id",
            "refunds_count",
        ],
        "account.payment.method.line": ["payment_acquirer_id", "payment_acquirer_state"],
        "payment.provider": ["journal_id"],
        "payment.transaction": ["payment_id", "invoice_ids", "invoices_count"],
    }
    for model, fields in moved_fields.items():
        for field in fields:
            util.move_field_to_module(cr, model, field, "payment", "account_payment")

    util.rename_field(cr, "account.payment.method.line", "payment_acquirer_id", "payment_provider_id")
    util.rename_field(cr, "account.payment.method.line", "payment_acquirer_state", "payment_provider_state")
