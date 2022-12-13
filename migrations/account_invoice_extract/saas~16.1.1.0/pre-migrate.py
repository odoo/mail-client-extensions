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
