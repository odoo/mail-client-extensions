from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "hr.expense", "extract_can_show_resend_button")

    util.remove_field(cr, "hr.expense", "extract_word_ids")
    util.remove_model(cr, "hr.expense.extract.words")
    util.rename_field(cr, "hr.expense", "state_processed", "extract_state_processed")

    # remove metadata because it is now coming from the mixin
    util.remove_field_metadata(cr, "hr.expense", "extract_can_show_send_button")
    util.remove_field_metadata(cr, "hr.expense", "extract_error_message")
    util.remove_field_metadata(cr, "hr.expense", "extract_remote_id")
    util.remove_field_metadata(cr, "hr.expense", "extract_state")
    util.remove_field_metadata(cr, "hr.expense", "extract_status_code")
    util.remove_field_metadata(cr, "hr.expense", "extract_state_processed")

    # compute new fields
    util.create_column(cr, "hr_expense", "is_in_extractable_state", "boolean", default=False)
    query = """
        UPDATE hr_expense
           SET is_in_extractable_state = true
         WHERE state = 'draft'
    """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="hr_expense"))
