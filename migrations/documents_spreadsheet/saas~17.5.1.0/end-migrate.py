from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "documents_spreadsheet.spreadsheet_cell_thread_write_rule", util.update_record_from_xml)
    util.if_unchanged(cr, "documents_spreadsheet.documents_document_thread_global_rule", util.update_record_from_xml)
    util.if_unchanged(cr, "documents_spreadsheet.spreadsheet_manager_document_threads", util.update_record_from_xml)
    util.if_unchanged(cr, "documents_spreadsheet.spreadsheet_manager_template_threads", util.update_record_from_xml)
    util.remove_record(cr, "documents_spreadsheet.spreadsheet_share_create_uid_rule")
    util.remove_record(cr, "documents_spreadsheet.spreadsheet_share_manager_rule")
