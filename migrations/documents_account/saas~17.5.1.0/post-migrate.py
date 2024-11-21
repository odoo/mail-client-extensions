from odoo.upgrade import util


def migrate(cr, version):
    server_actions = [
        "create_vendor_bill_code",
        "create_vendor_bill",
        "create_vendor_refund_code",
        "create_vendor_refund",
        "create_customer_invoice_code",
        "create_customer_invoice",
        "create_credit_note_code",
        "create_credit_note",
        "create_vendor_receipt",
        "create_misc_entry_code",
        "create_misc_entry",
        "bank_statement_code",
        "bank_statement",
        "create_customer_invoice",
        "create_credit_note_code",
        "create_credit_note",
    ]
    for action in server_actions:
        util.update_record_from_xml(cr, f"documents_account.ir_actions_server_{action}")
