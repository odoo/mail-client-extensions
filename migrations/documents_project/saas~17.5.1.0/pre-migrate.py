from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "documents_project.tag_view_form_inherit")

    util.remove_field(cr, "project.task", "shared_document_count")
    util.remove_field(cr, "project.task", "shared_document_ids")

    util.remove_field(cr, "project.project", "shared_document_count")
    util.remove_field(cr, "project.project", "shared_document_ids")

    # Add missing res_model, res_id for documents inside project folders
    # This aligns with new behavior of linked records and eases following steps
    # (which is also the reason why we also temporarily update folders too).
    # This is a bit complex because folders of different projects can be nested.
    util.explode_execute(
        cr,
        """
        WITH doc_project_id AS (
           SELECT d.id as document_id,
                  (ARRAY_AGG(
                    p.id ORDER BY (ARRAY_POSITION(STRING_TO_ARRAY(LEFT(d.parent_path, -1), '/'), f.id::text)) DESC
                  ))[1] as project_id
             FROM documents_document d
               -- match all folders in path
             JOIN documents_document f
               ON f.id::text = ANY(STRING_TO_ARRAY(LEFT(d.parent_path, -1), '/'))
               -- take only the folders linked to projects
             JOIN project_project p
               ON p.documents_folder_id = f.id
            WHERE COALESCE(d.res_model, 'documents.document') = 'documents.document'
              AND {parallel_filter}
         GROUP BY d.id
        )
        UPDATE documents_document d
           SET res_model = 'project.project',
               res_id = dp.project_id
          FROM doc_project_id dp
         WHERE d.id = dp.document_id
        """,
        table="documents_document",
        alias="d",
    )

    # Set access_internal and access_via_link_hidden based on project privacy_visibility
    util.explode_execute(
        cr,
        """
        WITH doc_with_project_privacy AS (
            SELECT d.id AS document_id,
                   BOOL_OR(p.privacy_visibility = 'followers') as is_followers
              FROM project_project p
         LEFT JOIN project_task t
                ON p.id = t.project_id
              JOIN documents_document d
                ON (res_model = 'project.project' AND res_id = p.id)
                OR (res_model = 'project.task' AND res_id = t.id)
               AND {parallel_filter}
          GROUP BY d.id
        )
        UPDATE documents_document document
           SET access_internal = CASE WHEN dp.is_followers THEN 'none' ELSE 'edit' END,
               is_access_via_link_hidden = CASE
                   WHEN dp.is_followers AND document.access_via_link != 'none' THEN TRUE
                   ELSE document.is_access_via_link_hidden  -- keep null if not access_via_link
               END
          FROM doc_with_project_privacy dp
          WHERE document.id = dp.document_id
        """,
        table="documents_document",
        alias="d",
    )

    # Create access_ids based on project privacy_visibility and followers for projects with
    # `privacy_visibility` = 'followers' (internal users) or 'portal' (portal users).

    # For all shared documents = all documents related to the project or any of its tasks
    # included in a former documents.share:
    #  * Set **projects** (portal) followers as project+task documents members
    #  * Set **task** (portal) followers as task-specific documents members

    util.explode_execute(
        cr,
        cr.mogrify(
            """
        WITH from_followers AS (
            SELECT d.id as document_id,
                   CASE p.privacy_visibility WHEN 'followers' THEN 'edit' ELSE 'view' END AS role,
                   f.partner_id as partner_id
              FROM project_project p
         LEFT JOIN project_task t
                ON p.id = t.project_id
              JOIN mail_followers f
                ON (f.res_model = 'project.project' AND f.res_id = p.id)
                OR (f.res_model = 'project.task' AND f.res_id = t.id)
              JOIN res_partner rp
                ON rp.id = f.partner_id
              JOIN documents_document d
                ON (d.res_model = f.res_model AND d.res_id = f.res_id)
                -- Match project followers with their task related documents too
                OR (    d.res_model = 'project.task' AND d.res_id = t.id
                    AND f.res_model = 'project.project' AND f.res_id = p.id)
             WHERE (   (p.privacy_visibility = 'followers' AND rp.partner_share IS NOT TRUE)
                    OR (p.privacy_visibility = 'portal' AND rp.partner_share IS TRUE))
               AND p.use_documents IS TRUE
               AND f.partner_id <> %s
               AND d._upg_was_shared IS TRUE
               AND {parallel_filter}
          GROUP BY d.id, p.privacy_visibility, f.partner_id
        )
        INSERT INTO documents_access (document_id, role, partner_id)
             SELECT ff.document_id, ff.role, ff.partner_id
               FROM from_followers ff
        -- because members could have been created with a generic step before this, better safe than sorry
        ON CONFLICT DO NOTHING
        """,
            [util.ref(cr, "base.partner_root")],
        ).decode(),
        table="documents_document",
        alias="d",
    )

    # Remove project/task res_model, res_id on folders
    util.explode_execute(
        cr,
        """
        UPDATE documents_document d
           SET res_model = NULL,
               res_id = NULL
         WHERE type = 'folder'
           AND res_model IN ('project.project', 'project.task')
           AND {parallel_filter}
        """,
        table="documents_document",
        alias="d",
    )
