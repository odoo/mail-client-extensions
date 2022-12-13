# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "hr.applicant", "extract_can_show_resend_button")
    util.rename_field(cr, "hr.applicant", "is_first_stage", "is_in_extractable_state")
    util.rename_field(cr, "hr.applicant", "state_processed", "extract_state_processed")

    # remove metadata because it is now coming from the mixin
    util.remove_field_metadata(cr, "hr.applicant", "extract_can_show_send_button")
    util.remove_field_metadata(cr, "hr.applicant", "extract_error_message")
    util.remove_field_metadata(cr, "hr.applicant", "extract_remote_id")
    util.remove_field_metadata(cr, "hr.applicant", "extract_state")
    util.remove_field_metadata(cr, "hr.applicant", "extract_status_code")
