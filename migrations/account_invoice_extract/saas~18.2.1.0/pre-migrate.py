from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "account.move", "extract_word_ids", "extracted_word_ids")
    query = """
        DELETE FROM ir_model_data
              WHERE module = 'account_invoice_extract'
                AND name IN ('field_account_bank_statement_line__extract_attachment_id',
                              'field_account_bank_statement_line__extracted_word_ids')
    """
    cr.execute(query)
