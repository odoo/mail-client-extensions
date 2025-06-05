from odoo.upgrade import util


def migrate(cr, version):
    util.delete_unused(
        cr,
        "documents_account.ir_actions_server_create_vendor_bill_tag_remove_to_validate",
        "documents_account.ir_actions_server_create_vendor_bill_tag_remove_inbox"
        "documents_account.ir_actions_server_create_vendor_bill_tag_add_validated",
        "documents_account.ir_actions_server_create_vendor_bill_tag_add_bill",
        "documents_account.ir_actions_server_create_vendor_refund_tag_remove_inbox",
        "documents_account.ir_actions_server_create_vendor_refund_tag_remove_to_validate",
        "documents_account.ir_actions_server_create_vendor_refund_tag_add_validated",
        "documents_account.ir_actions_server_create_vendor_refund_tag_add_bill",
        "documents_account.ir_actions_server_create_customer_invoice_tag_remove_inbox",
        "documents_account.ir_actions_server_create_customer_invoice_tag_remove_to_validate",
        "documents_account.ir_actions_server_create_customer_invoice_tag_add_validated",
        "documents_account.ir_actions_server_create_customer_invoice_tag_add_bill",
        "documents_account.ir_actions_server_create_credit_note_tag_remove_inbox",
        "documents_account.ir_actions_server_create_credit_note_tag_remove_to_validate",
        "documents_account.ir_actions_server_create_credit_note_tag_add_validated",
        "documents_account.ir_actions_server_create_credit_note_tag_add_bill",
        "documents_account.ir_actions_server_create_misc_entry_tag_add_validated",
        "documents_account.ir_actions_server_create_misc_entry_tag_remove_inbox",
        "documents_account.ir_actions_server_create_misc_entry_tag_remove_to_validate",
        "documents_account.ir_actions_server_bank_statement_tag_add_validated",
        "documents_account.ir_actions_server_bank_statement_tag_remove_inbox",
        "documents_account.ir_actions_server_bank_statement_tag_remove_to_validate",
    )
