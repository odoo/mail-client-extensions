from odoo.upgrade import util


def migrate(cr, version):
    # As the bridge now works as 'documents related to a project are in the project folder', we:
    # 1. Add a tag on documents located outside their project folder so they can be searched
    # conveniently.
    util.create_column(cr, "documents_document", "_upg_181_outside_project_folder_tag_name", "varchar")
    util.create_column(cr, "documents_document", "_upg_181_opf_project_folder_id", "int")
    util.create_index(cr, "_upg_181_opf_tag_name_idx", "documents_document", "_upg_181_outside_project_folder_tag_name")
    util.create_index(cr, "_upg_181_opf_project_folder_id_idx", "documents_document", "_upg_181_opf_project_folder_id")

    util.explode_execute(
        cr,
        """
        WITH docs_outside_project_folder AS (
            SELECT d.id AS document_id,
                   p.documents_folder_id AS project_folder_id,
                   p.name->>'en_US' AS tag_name
              FROM documents_document d
              JOIN project_project p
                ON d.res_model = 'project.project'
               AND d.res_id = p.id
               AND d.shortcut_document_id IS NULL
               AND d.type != 'folder'
               AND p.use_documents
               AND p.documents_folder_id::text != ALL(STRING_TO_ARRAY(d.parent_path, '/'))
               AND {parallel_filter}

             UNION

            SELECT d.id AS document_id,
                   p.documents_folder_id as project_folder_id,
                   p.name->>'en_US' || ': ' || t.name AS tag_name
              FROM documents_document d
              JOIN project_task t
                ON d.res_model = 'project.task'
               AND d.res_id = t.id
               AND d.shortcut_document_id IS NULL
               AND d.type != 'folder'
              JOIN project_project p
                ON p.id = t.project_id
               AND p.use_documents
               AND p.documents_folder_id::text != ALL(STRING_TO_ARRAY(d.parent_path, '/'))
               AND {parallel_filter}
        )
        UPDATE documents_document d
           SET _upg_181_outside_project_folder_tag_name = tag_name,
               _upg_181_opf_project_folder_id = docs_outside_project_folder.project_folder_id
          FROM docs_outside_project_folder
         WHERE d.id = docs_outside_project_folder.document_id
     RETURNING d.id
        """,
        table="documents_document",
        alias="d",
    )

    if not cr.rowcount:
        util.remove_column(cr, "documents_document", "_upg_181_outside_project_folder_tag_name")
        util.remove_column(cr, "documents_document", "_upg_181_opf_project_folder_id")
        return

    if cr.rowcount > 100:
        raise util.MigrationError("Documents [Project]: Too many shortcuts to create, further investigation required.")

    cr.execute(
        """
        INSERT INTO documents_tag (name, color, sequence)
             SELECT JSONB_BUILD_OBJECT('en_US', _upg_181_outside_project_folder_tag_name), 1, 1000
               FROM documents_document
              WHERE _upg_181_outside_project_folder_tag_name IS NOT NULL
           GROUP BY _upg_181_outside_project_folder_tag_name
        ON CONFLICT DO NOTHING
        """
    )
    cr.execute(
        """
        INSERT INTO document_tag_rel (documents_document_id, documents_tag_id)
             SELECT d.id, t.id
               FROM documents_document d
               JOIN documents_tag t
                 ON d._upg_181_outside_project_folder_tag_name = t.name->>'en_US'
        ON CONFLICT DO NOTHING
        """
    )
    util.remove_column(cr, "documents_document", "_upg_181_outside_project_folder_tag_name")
    cr.execute(
        """
        SELECT d._upg_181_opf_project_folder_id,
               ARRAY_AGG(d.id) as doc_ids
          FROM documents_document d
          JOIN documents_document pf
            ON d._upg_181_opf_project_folder_id = pf.id
         WHERE pf.active
      GROUP BY d._upg_181_opf_project_folder_id
        """
    )
    res = cr.fetchall()
    util.remove_column(cr, "documents_document", "_upg_181_opf_project_folder_id")

    # 2. Create shortcut inside the project folder for each document linked but located outside it.
    for destination_id, document_ids in res:
        for docs in util.iter_browse(util.env(cr)["documents.document"], document_ids, strategy="commit"):
            docs.action_create_shortcut(location_folder_id=destination_id)

    # 3. Remove all res_model, res_id values for all documents to show that we don't use this link anymore
    util.explode_execute(
        cr,
        """
        UPDATE documents_document d
           SET res_model = NULL,
               res_id = NULL
         WHERE res_model in ('project.project', 'project.task')
           AND {parallel_filter}
        """,
        table="documents_document",
        alias="d",
    )
