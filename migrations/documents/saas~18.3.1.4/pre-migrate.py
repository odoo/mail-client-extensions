from odoo.upgrade import util


def migrate(cr, version):
    if util.module_installed(cr, "documents_fsm"):
        util.move_field_to_module(cr, "documents.document", "document_count", "documents", "documents_fsm")
    else:
        util.remove_field(cr, "documents.document", "document_count")

    util.remove_field(cr, "documents.document", "is_locked")
    util.remove_view(cr, "documents.document_view_form")
    util.remove_view(cr, "documents.document_view_form_details")

    cr.execute("ALTER TABLE documents_document ALTER COLUMN alias_id DROP NOT NULL")
    cr.execute("CREATE INDEX ON documents_document(alias_id) WHERE alias_id IS NOT NULL")
    cr.commit()
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
            UPDATE documents_document d
               SET alias_id = NULL
              FROM non_folders f
             WHERE d.id = f.id
        ),
        delete_aliases AS (
            DELETE
              FROM mail_alias a
             USING non_folders f
            WHERE a.id  = f.alias_id
        )
        DELETE
          FROM document_alias_tag_rel r
         USING non_folders f
         WHERE r.documents_document_id = f.id
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
