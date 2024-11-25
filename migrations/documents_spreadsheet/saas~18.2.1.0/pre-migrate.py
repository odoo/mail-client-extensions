from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "res.config.settings", "document_spreadsheet_folder_id")
    util.remove_field(cr, "res.company", "document_spreadsheet_folder_id")

    spreadsheet_folder_id = util.ref(cr, "documents_spreadsheet.document_spreadsheet_folder")
    cr.execute("SELECT count(id) FROM documents_document WHERE folder_id = %s", (spreadsheet_folder_id,))
    (has_spreadsheet_folder_document,) = cr.fetchone()
    if not has_spreadsheet_folder_document:
        util.delete_unused(cr, "documents_spreadsheet.document_spreadsheet_folder")
    else:
        cr.execute(
            "DELETE FROM ir_model_data WHERE module='documents_spreadsheet' AND name='document_spreadsheet_folder'"
        )
