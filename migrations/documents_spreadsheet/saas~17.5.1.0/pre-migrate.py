from odoo.upgrade import util

documents_pre_migrate = util.import_script("documents/saas~17.5.1.4/pre-migrate.py")


def migrate(cr, version):
    # Migrate frozen spreadsheet on share, only if there's 1 and only 1 spreadsheet
    # (because the token can not be reused)

    # let the ORM create the alias
    cr.execute("ALTER TABLE documents_document ALTER COLUMN alias_id DROP NOT NULL")
    cr.execute("ALTER TABLE documents_document ALTER COLUMN document_token DROP NOT NULL")

    util.create_column(
        cr,
        "documents_document",
        "_upg_old_shared_spreadsheet_id",
        "int4",
    )

    frozen_spreadsheets = """
    WITH frozen_spreadsheets AS (
       SELECT min(shared_spreadsheet.document_id) AS id,
              share.access_token,
              min(shared_spreadsheet.id) AS documents_shared_spreadsheet_id
         FROM documents_shared_spreadsheet AS shared_spreadsheet
         JOIN documents_share AS share
           ON share.id = shared_spreadsheet.share_id
     GROUP BY shared_spreadsheet.share_id, share.access_token, share.alias_id
       HAVING COUNT(shared_spreadsheet.document_id) = 1
    )
    """

    # create the frozen spreadsheet folder
    cr.execute(
        frozen_spreadsheets
        + """
            INSERT INTO documents_document (
                    name, type, handler, folder_id, owner_id,
                    access_via_link, access_internal, active, parent_path
            )
             SELECT DISTINCT ON (doc.folder_id)
                    'Frozen spreadsheets',  -- TODO: should we translate the name ?
                    'folder',
                    'frozen_folder',
                    doc.folder_id,
                    %(odoobot)s,
                    'none',
                    'none',
                    TRUE,
                    COALESCE(folder.parent_path, '') -- start with folder when we don't know the id
               FROM frozen_spreadsheets
               JOIN documents_document AS doc
                 ON doc.id = frozen_spreadsheets.id
          LEFT JOIN documents_document as folder
                 ON folder.id = doc.folder_id
          RETURNING id
        """,
        {"odoobot": util.ref(cr, "base.user_root")},
    )

    ids_to_update = [r[0] for r in cr.fetchall()]
    cr.execute(
        """
        UPDATE documents_document
           SET parent_path = concat(parent_path, id, '/')
         WHERE id = ANY(%(new_folder_ids)s)
        """,
        {"new_folder_ids": ids_to_update},
    )

    documents_pre_migrate.fix_missing_document_tokens(cr)

    # create one document per frozen spreadsheet in that folder
    cr.execute(
        frozen_spreadsheets
        + """
        INSERT INTO documents_document (
                    name, type, handler, folder_id, parent_path, owner_id, document_token,
                    access_via_link, access_internal, is_access_via_link_hidden, active,
                    _upg_old_shared_spreadsheet_id, attachment_id
        )
             SELECT 'Frozen: ' || spreadsheet.name,  -- TODO: should we translate the name ?
                    'binary',
                    'frozen_spreadsheet',
                    frozen_folder.id,
                    frozen_folder.parent_path,
                    spreadsheet.owner_id,
                    frozen.access_token,  -- temporary keep the token to ease the migration to documents_redirect
                    'view',
                    'none',
                    TRUE,
                    TRUE,
                    documents_shared_spreadsheet_id,
                    attachment.id
               FROM frozen_spreadsheets AS frozen
               JOIN documents_document AS spreadsheet
                 ON spreadsheet.id = frozen.id
               JOIN documents_document AS frozen_folder
                 ON frozen_folder.folder_id = spreadsheet.folder_id
                AND frozen_folder.handler = 'frozen_folder'
          LEFT JOIN ir_attachment AS attachment
                 ON attachment.res_model = 'documents.shared.spreadsheet'
                AND attachment.res_field = 'spreadsheet_binary_data'
                AND attachment.res_id = documents_shared_spreadsheet_id
          RETURNING id
        """,
        {"odoobot": util.ref(cr, "base.user_root")},
    )

    ids_to_update = [r[0] for r in cr.fetchall()]
    cr.execute(
        """
        UPDATE documents_document
           SET parent_path = concat(parent_path, id, '/')
         WHERE id = ANY(%(new_document_ids)s)
        """,
        {"new_document_ids": ids_to_update},
    )

    # Create an alias for the newly created documents
    documents_pre_migrate.fix_missing_alias_ids(cr)

    # move excel_export, datas, ... from <documents.shared.spreadsheet> to <documents.document>
    util.explode_execute(
        cr,
        """
        UPDATE ir_attachment
           SET res_model = 'documents.document',
               res_id = frozen_spreadsheet.id,
               res_field = (
                   CASE WHEN ir_attachment.res_field = 'spreadsheet_binary_data'
                        THEN NULL
                        ELSE ir_attachment.res_field
                         END
               ),
               name = (
                   CASE WHEN ir_attachment.name = 'spreadsheet_binary_data'
                        THEN frozen_spreadsheet.name
                        ELSE ir_attachment.name
                         END
               )
          FROM documents_document AS frozen_spreadsheet
         WHERE frozen_spreadsheet.handler = 'frozen_spreadsheet'
           AND ir_attachment.res_model = 'documents.shared.spreadsheet'
           AND ir_attachment.res_id = frozen_spreadsheet._upg_old_shared_spreadsheet_id
           AND {parallel_filter}
        """,
        table="documents_document",
        alias="frozen_spreadsheet",
    )

    documents_pre_migrate.fix_missing_document_tokens(cr)

    # Move token from `documents.document` to `document.redirect`
    util.explode_execute(
        cr,
        """
     INSERT INTO documents_redirect (document_id, access_token)
          SELECT document.id,
                 document.document_token
            FROM documents_document AS document
           WHERE document.handler = 'frozen_spreadsheet'
             AND {parallel_filter}
         """,
        table="documents_document",
        alias="document",
    )

    # Now that the tokens have been moved to `documents_redirect`, reset the token on the `documents_document` table
    cr.execute("UPDATE documents_document SET document_token = NULL WHERE handler = 'frozen_spreadsheet'")
    documents_pre_migrate.fix_missing_document_tokens(cr)

    cr.execute("ALTER TABLE documents_document ALTER COLUMN document_token SET NOT NULL")

    # Standard spreadsheet have been redirected in `documents.redirect`,
    # in the main documents migration script, we only want to keep frozen spreadsheet
    cr.execute(
        """
        DELETE FROM documents_redirect
              USING documents_document
              WHERE documents_document.handler = 'spreadsheet'
                AND documents_redirect.document_id = documents_document.id
        """
    )

    util.rename_field(
        cr,
        "res.company",
        "documents_spreadsheet_folder_id",
        "document_spreadsheet_folder_id",
    )
    util.rename_field(
        cr,
        "res.config.settings",
        "documents_spreadsheet_folder_id",
        "document_spreadsheet_folder_id",
    )

    util.remove_model(cr, "documents.shared.spreadsheet")
    util.remove_column(cr, "documents_document", "_upg_old_shared_spreadsheet_id")

    xmlid_mapping = {
        "documents_spreadsheet_folder": "document_spreadsheet_folder",
    }
    documents_pre_migrate.migrate_folders_xmlid(cr, "documents_project", xmlid_mapping)
