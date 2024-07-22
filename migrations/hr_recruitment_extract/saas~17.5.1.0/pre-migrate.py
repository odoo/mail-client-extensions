from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "hr_candidate", "extract_state", "varchar")
    util.create_column(cr, "hr_candidate", "extract_status", "varchar")
    util.create_column(cr, "hr_candidate", "extract_document_uuid", "varchar")
    util.create_column(cr, "hr_candidate", "is_in_extractable_state", "boolean")
    util.create_column(cr, "hr_candidate", "extract_state_processed", "boolean")

    cr.execute(
        """
        UPDATE hr_candidate
           SET extract_state = hr_applicant.extract_state,
               extract_status = hr_applicant.extract_status,
               extract_document_uuid = hr_applicant.extract_document_uuid,
               is_in_extractable_state = hr_applicant.is_in_extractable_state,
               extract_state_processed = hr_applicant.extract_state_processed
          FROM hr_applicant
         WHERE hr_candidate.id = hr_applicant.candidate_id
        """
    )

    util.remove_field(cr, "hr.applicant", "extract_state")
    util.remove_field(cr, "hr.applicant", "extract_status")
    util.remove_field(cr, "hr.applicant", "extract_error_message")
    util.remove_field(cr, "hr.applicant", "extract_document_uuid")
    util.remove_field(cr, "hr.applicant", "extract_can_show_send_button")
    util.remove_field(cr, "hr.applicant", "is_in_extractable_state")
    util.remove_field(cr, "hr.applicant", "extract_state_processed")
