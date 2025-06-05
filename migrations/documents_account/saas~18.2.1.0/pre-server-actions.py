from odoo.upgrade import util


def migrate(cr, version):
    """
    Here we try to match changes from this module xml data.

    Here's this module `multi` server actions, along with their children and a [TAG] if changed:
    - `documents_account.ir_actions_server_create_vendor_bill`
        - [NEW] `documents_account.ir_actions_server_create_vendor_bill_tag_remove_inbox`
        - [NEW] `documents_account.ir_actions_server_create_vendor_bill_tag_remove_to_validate`
        - [NEW] `documents_account.ir_actions_server_create_vendor_bill_tag_add_validated`
        - [NEW] `documents_account.ir_actions_server_create_vendor_bill_tag_add_bill`
        - `documents_account.ir_actions_server_create_vendor_bill_code`

    - `documents_account.ir_actions_server_create_vendor_refund`
        - [NEW] `documents_account.ir_actions_server_create_vendor_refund_tag_remove_inbox`
        - [NEW] `documents_account.ir_actions_server_create_vendor_refund_tag_remove_to_validate`
        - [NEW] `documents_account.ir_actions_server_create_vendor_refund_tag_add_validated`
        - [NEW] `documents_account.ir_actions_server_create_vendor_refund_tag_add_bill`
        - `documents_account.ir_actions_server_create_vendor_refund_code`

    - `documents_account.ir_actions_server_create_customer_invoice`
        - [NEW] `documents_account.ir_actions_server_create_customer_invoice_tag_remove_inbox`
        - [NEW] `documents_account.ir_actions_server_create_customer_invoice_tag_remove_to_validate`
        - [NEW] `documents_account.ir_actions_server_create_customer_invoice_tag_add_validated`
        - [NEW] `documents_account.ir_actions_server_create_customer_invoice_tag_add_bill`
        - `documents_account.ir_actions_server_create_customer_invoice_code`

    - `documents_account.ir_actions_server_create_credit_note`
        - [NEW] `documents_account.ir_actions_server_create_credit_note_tag_remove_inbox`
        - [NEW] `documents_account.ir_actions_server_create_credit_note_tag_remove_to_validate`
        - [NEW] `documents_account.ir_actions_server_create_credit_note_tag_add_validated`
        - [NEW] `documents_account.ir_actions_server_create_credit_note_tag_add_bill`
        - `documents_account.ir_actions_server_create_credit_note_code`

    - `documents_account.ir_actions_server_create_misc_entry`
        - [NEW] `documents_account.ir_actions_server_create_misc_entry_tag_add_validated`
        - [NEW] `documents_account.ir_actions_server_create_misc_entry_tag_remove_inbox`
        - [NEW] `documents_account.ir_actions_server_create_misc_entry_tag_remove_to_validate`
        - `documents_account.ir_actions_server_create_misc_entry_code`

    - `documents_account.ir_actions_server_bank_statement`
        - [NEW] `documents_account.ir_actions_server_bank_statement_tag_add_validated`
        - [NEW] `documents_account.ir_actions_server_bank_statement_tag_remove_inbox`
        - [NEW] `documents_account.ir_actions_server_bank_statement_tag_remove_to_validate`
        - `documents_account.ir_actions_server_bank_statement_code`
    """

    # dict shape: { parent: { new: origin }}
    child_xmlids_changes_by_parent = {
        "documents_account.ir_actions_server_create_vendor_bill": {
            "documents_account.ir_actions_server_create_vendor_bill_tag_remove_inbox": "documents.ir_actions_server_tag_remove_inbox",
            "documents_account.ir_actions_server_create_vendor_bill_tag_remove_to_validate": "documents.ir_actions_server_tag_remove_to_validate",
            "documents_account.ir_actions_server_create_vendor_bill_tag_add_validated": "documents.ir_actions_server_tag_add_validated",
            "documents_account.ir_actions_server_create_vendor_bill_tag_add_bill": "documents.ir_actions_server_tag_add_bill",
        },
        "documents_account.ir_actions_server_create_vendor_refund": {
            "documents_account.ir_actions_server_create_vendor_refund_tag_remove_inbox": "documents.ir_actions_server_tag_remove_inbox",
            "documents_account.ir_actions_server_create_vendor_refund_tag_remove_to_validate": "documents.ir_actions_server_tag_remove_to_validate",
            "documents_account.ir_actions_server_create_vendor_refund_tag_add_validated": "documents.ir_actions_server_tag_add_validated",
            "documents_account.ir_actions_server_create_vendor_refund_tag_add_bill": "documents.ir_actions_server_tag_add_bill",
        },
        "documents_account.ir_actions_server_create_customer_invoice": {
            "documents_account.ir_actions_server_create_customer_invoice_tag_remove_inbox": "documents.ir_actions_server_tag_remove_inbox",
            "documents_account.ir_actions_server_create_customer_invoice_tag_remove_to_validate": "documents.ir_actions_server_tag_remove_to_validate",
            "documents_account.ir_actions_server_create_customer_invoice_tag_add_validated": "documents.ir_actions_server_tag_add_validated",
            "documents_account.ir_actions_server_create_customer_invoice_tag_add_bill": "documents.ir_actions_server_tag_add_bill",
        },
        "documents_account.ir_actions_server_create_credit_note": {
            "documents_account.ir_actions_server_create_credit_note_tag_remove_inbox": "documents.ir_actions_server_tag_remove_inbox",
            "documents_account.ir_actions_server_create_credit_note_tag_remove_to_validate": "documents.ir_actions_server_tag_remove_to_validate",
            "documents_account.ir_actions_server_create_credit_note_tag_add_validated": "documents.ir_actions_server_tag_add_validated",
            "documents_account.ir_actions_server_create_credit_note_tag_add_bill": "documents.ir_actions_server_tag_add_bill",
        },
        "documents_account.ir_actions_server_create_misc_entry": {
            "documents_account.ir_actions_server_create_misc_entry_tag_add_validated": "documents.ir_actions_server_tag_add_validated",
            "documents_account.ir_actions_server_create_misc_entry_tag_remove_inbox": "documents.ir_actions_server_tag_remove_inbox",
            "documents_account.ir_actions_server_create_misc_entry_tag_remove_to_validate": "documents.ir_actions_server_tag_remove_to_validate",
        },
        "documents_account.ir_actions_server_bank_statement": {
            "documents_account.ir_actions_server_bank_statement_tag_add_validated": "documents.ir_actions_server_tag_add_validated",
            "documents_account.ir_actions_server_bank_statement_tag_remove_inbox": "documents.ir_actions_server_tag_remove_inbox",
            "documents_account.ir_actions_server_bank_statement_tag_remove_to_validate": "documents.ir_actions_server_tag_remove_to_validate",
        },
    }
    util.import_script("base/saas~18.2.1.3/pre-ir_act_server.py").rematch_xmlids(
        cr, child_xmlids_changes_by_parent, mute_missing_child=True
    )
    cr.execute(
        """
        DELETE
          FROM ir_act_server_group_rel
         WHERE gid = %s
           AND act_id = %s
         """,
        [util.ref(cr, "base.group_user"), util.ref(cr, "documents_account.ir_actions_server_create_vendor_bill_code")],
    )
