from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "documents_account.ir_actions_server_create_vendor_bill_code", util.update_record_from_xml)
    util.if_unchanged(cr, "documents_account.ir_actions_server_create_vendor_refund_code", util.update_record_from_xml)
    util.if_unchanged(
        cr, "documents_account.ir_actions_server_create_customer_invoice_code", util.update_record_from_xml
    )
    util.if_unchanged(cr, "documents_account.ir_actions_server_create_credit_note_code", util.update_record_from_xml)
    util.if_unchanged(cr, "documents_account.ir_actions_server_create_vendor_receipt", util.update_record_from_xml)
    util.if_unchanged(cr, "documents_account.ir_actions_server_create_misc_entry_code", util.update_record_from_xml)
    util.if_unchanged(cr, "documents_account.ir_actions_server_bank_statement_code", util.update_record_from_xml)
