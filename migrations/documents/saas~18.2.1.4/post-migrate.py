from odoo.upgrade import util


def migrate(cr, version):
    internal_folder = util.env(cr)["documents.document"].browse(util.ref(cr, "documents.document_internal_folder"))
    if internal_folder and internal_folder.name == "Internal":
        internal_folder.name = "Administrative"
    util.if_unchanged(cr, "documents.mail_template_document_request", util.update_record_from_xml)
    util.if_unchanged(cr, "documents.mail_template_document_request_reminder", util.update_record_from_xml)
