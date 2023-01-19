# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "account.move", "extract_can_show_resend_button")
    util.remove_record(cr, "account_invoice_extract.account_invoice_extract_no_credit")

    # remove metadata because it is now coming from the mixin
    util.remove_field_metadata(cr, "account.move", "extract_can_show_send_button")
    util.remove_field_metadata(cr, "account.move", "extract_error_message")
    util.remove_field_metadata(cr, "account.move", "extract_remote_id")
    util.remove_field_metadata(cr, "account.move", "extract_state")
    util.remove_field_metadata(cr, "account.move", "extract_status_code")

    # compute new fields
    util.create_column(cr, "account_move", "extract_state_processed", "boolean", default=False)
    query = """
        UPDATE account_move
           SET extract_state_processed = true
         WHERE extract_state IN ('waiting_extraction', 'waiting_upload')
    """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="account_move"))

    util.create_column(cr, "account_move", "is_in_extractable_state", "boolean", default=False)
    query = """
        UPDATE account_move
           SET is_in_extractable_state = true
         WHERE state = 'draft'
    """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="account_move"))
