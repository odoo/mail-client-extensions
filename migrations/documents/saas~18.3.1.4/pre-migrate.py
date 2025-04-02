from odoo.upgrade import util


def migrate(cr, version):
    if util.module_installed(cr, "documents_fsm"):
        util.move_field_to_module(cr, "documents.document", "document_count", "documents", "documents_fsm")
    else:
        util.remove_field(cr, "documents.document", "document_count")

    util.remove_field(cr, "documents.document", "is_locked")
    util.remove_view(cr, "documents.document_view_form")
    util.remove_view(cr, "documents.document_view_form_details")

    mapping = {
        util.ref(cr, "documents.mail_documents_activity_data_tv"): util.ref(cr, "mail.mail_activity_data_todo"),
        util.ref(cr, "documents.mail_documents_activity_data_md"): util.ref(
            cr, "mail.mail_activity_data_upload_document"
        ),
    }
    util.replace_record_references_batch(
        cr,
        mapping,
        "mail.activity.type",
        replace_xmlid=False,
    )
    util.delete_unused(cr, "documents.mail_documents_activity_data_tv", "documents.mail_documents_activity_data_md")
