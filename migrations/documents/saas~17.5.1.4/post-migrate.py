from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "documents.mail_template_document_request", util.update_record_from_xml)
    util.if_unchanged(cr, "documents.mail_template_document_request_reminder", util.update_record_from_xml)
    util.if_unchanged(cr, "documents.public_page_layout", util.update_record_from_xml)

    # The `name` of documents tags is unique in 18.0.
    # The record in documents.projects has been deleted in 18.0
    # And a new one was added in documents.
    # Since the record is `forcecreate=0`, dependant modules installed
    # during or after the upgrade will fail, so we update it and force create it.
    util.rename_xmlid(cr, "documents_project.documents_project_status_draft", "documents.documents_tag_draft")
    util.update_record_from_xml(cr, "documents.documents_tag_draft")
