from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "documents.mail_template_document_request", util.update_record_from_xml)
    util.if_unchanged(cr, "documents.mail_template_document_request_reminder", util.update_record_from_xml)
    util.if_unchanged(cr, "documents.public_page_layout", util.update_record_from_xml)
