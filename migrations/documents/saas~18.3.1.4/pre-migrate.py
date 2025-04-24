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

    cr.execute("ALTER TABLE documents_document ALTER COLUMN alias_id DROP NOT NULL")
    util.explode_execute(
        cr,
        """
        WITH non_folders AS (
            SELECT id, alias_id
              FROM documents_document d
             WHERE d.type != 'folder'
               AND {parallel_filter}
        ),
        clear_alias_ids AS (
            UPDATE documents_document
               SET alias_id = NULL
             WHERE id IN (SELECT id FROM non_folders)
        ),
        delete_aliases AS (
            DELETE FROM mail_alias WHERE id IN (SELECT alias_id FROM non_folders)
        )
        DELETE FROM document_alias_tag_rel WHERE documents_document_id IN (SELECT id FROM non_folders)
    """,
        alias="d",
        table="documents_document",
    )

    # Remove `alias.mixin` "inherits" fields
    util.remove_field(cr, "documents.document", "alias_status")
    util.remove_field(cr, "documents.document", "alias_bounced_content")
    util.remove_field(cr, "documents.document", "alias_incoming_local")
    util.remove_field(cr, "documents.document", "alias_contact")
    util.remove_field(cr, "documents.document", "alias_parent_thread_id")
    util.remove_field(cr, "documents.document", "alias_parent_model_id")
    util.remove_field(cr, "documents.document", "alias_force_thread_id")
    util.remove_field(cr, "documents.document", "alias_model_id")
    util.remove_field(cr, "documents.document", "alias_full_name")
