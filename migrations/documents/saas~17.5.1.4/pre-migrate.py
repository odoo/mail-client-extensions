import ast
import base64
import contextlib
import uuid
from collections import defaultdict
from os import getenv

import psycopg2
from psycopg2 import sql
from psycopg2.extras import execute_values

from odoo.upgrade import util
from odoo.upgrade.util.inconsistencies import break_recursive_loops

FOLDERS_GROUPS_MAX_MEMBERS = 49
DOCUMENTS_FOLDERS_LARGE_GROUPS_RIGHTS_OPTIONS = {"SET_NOBODY", "SET_USER_SPECIFIC", "ACCEPT_AS_IS"}


def migrate(cr, version):
    ###################
    # DOCUMENTS.FACET #
    ###################

    util.create_column(cr, "documents_tag", "color", "int4")
    if util.column_exists(cr, "documents_facet", "color"):
        # The tags take the color of its facet
        cr.execute(
            """
            UPDATE documents_tag tag
               SET color = facet.color
              FROM documents_facet AS facet
             WHERE facet.id = tag.facet_id
            """
        )

    ######################
    # DOCUMENTS.DOCUMENT #
    ######################

    util.remove_field(cr, "documents.document", "create_share_id")
    util.change_field_selection_values(cr, "documents.document", "type", {"empty": "binary"})

    #####################
    # DOCUMENTS.FOLDERS #
    #####################

    # new <documents.document> fields
    util.create_column(cr, "documents_document", "is_access_via_link_hidden", "boolean")
    util.create_column(cr, "documents_document", "is_pinned_folder", "boolean")
    util.create_column(cr, "documents_document", "company_id", "int4")
    util.create_column(cr, "documents_document", "document_token", "varchar")
    util.create_column(cr, "documents_document", "access_via_link", "varchar")
    util.create_column(cr, "documents_document", "access_internal", "varchar")
    util.create_column(cr, "documents_document", "parent_path", "varchar")
    util.create_column(cr, "documents_document", "alias_id", "int4")  # mail.alias.mixin
    util.create_column(cr, "documents_document", "create_activity_option", "boolean")
    util.create_column(cr, "documents_document", "create_activity_type_id", "int4")
    util.create_column(cr, "documents_document", "create_activity_summary", "varchar")
    util.create_column(cr, "documents_document", "create_activity_date_deadline_range", "int4")
    util.create_column(cr, "documents_document", "create_activity_date_deadline_range_type", "varchar")
    util.create_column(cr, "documents_document", "create_activity_note", "varchar")
    util.create_column(cr, "documents_document", "create_activity_user_id", "int4")

    util.create_column(cr, "documents_document", "_upg_was_shared", "boolean")

    # Root folders will have NULL folder_id when we transform them into documents
    cr.execute("ALTER TABLE documents_document ALTER COLUMN folder_id DROP NOT NULL")
    util.create_column(cr, "documents_document", "_upg_old_folder_id", "int4")
    util.create_column(cr, "documents_folder", "_upg_new_folder_id", "int4")

    internal_id = util.ref(cr, "base.group_user")

    check_or_raise_large_groups(cr, internal_id)

    # Avoid unique constraints failures during update
    cr.execute("ALTER TABLE documents_folder_read_groups DROP CONSTRAINT IF EXISTS documents_folder_read_groups_pkey")
    cr.execute(
        "ALTER TABLE documents_folder_res_groups_rel DROP CONSTRAINT IF EXISTS documents_folder_res_groups_rel_pkey"
    )

    # Before:
    #
    # documents_document          documents_folder
    # folder_id -------FK-------> id <-----------------+
    #                             parent_folder_id -FK-+
    #
    # After the insert query below we'll have new records with:
    #
    # documents_document          documents_folder
    # _upgrade_old_folder_id <--- id
    # folder_id <---------------- parent_folder_id
    #
    # When we update all FKs pointing to documents_folder we also
    # update the reference documents_document via folder_id:
    #
    # document_documents          documents_document
    # folder_id ----------------> upg_old_folder_id
    #        ^-----SET----------- id
    #
    # In other words documents_document.folder_id will correctly point
    # to the new record in document_documents corresponding to the
    # former documents_folder
    lang_code = util.env(cr)["res.company"]._get_main_company().partner_id.lang or "en_US"
    cr.execute(
        """
        WITH new_folder_ids AS (
            INSERT INTO documents_document (
                    _upg_old_folder_id, name, type, res_id, res_model,
                    active, parent_path, company_id, folder_id
                 )
                 SELECT folder.id, COALESCE(folder.name->>partner.lang, folder.name->>%s, folder.name->>'en_US'),
                        'folder', NULL, NULL,
                        folder.active, NULL, folder.company_id, folder.parent_folder_id
                   FROM documents_folder folder
              LEFT JOIN res_company company
                     ON company.id = folder.company_id
              LEFT JOIN res_partner partner
                     ON partner.id = company.partner_id
              RETURNING id, _upg_old_folder_id
        )
        UPDATE documents_folder
           SET _upg_new_folder_id = new_folder_ids.id
          FROM documents_folder f
          JOIN new_folder_ids
            ON new_folder_ids._upg_old_folder_id = f.id
         WHERE documents_folder.id = f.id
        """,
        [lang_code],
    )

    # documents_share will be used during the upgrade, keep the reference to documents_folder
    util.remove_constraint(cr, "documents_share", "documents_share_folder_id_fkey")

    cr.execute("ALTER TABLE documents_facet DROP CONSTRAINT IF EXISTS documents_facet_name_unique")

    # replace all FKs to documents_folder by the new documents_document
    actions_map = {"a": "NO ACTION", "r": "RESTRICT", "c": "CASCADE", "n": "SET NULL", "d": "SET DEFAULT"}
    for table, column, constraint_name, action in util.get_fk(cr, "documents_folder", quote_ident=False):
        if table == "documents_folder":
            # do not update self references, the documents.folder model will be removed anyway
            # custom references need to be handled post upgrade
            continue
        cr.execute(util.format_query(cr, "ALTER TABLE {} DROP CONSTRAINT {}", table, constraint_name))

        new_index = f"_upg_{table}_{column}"
        cr.execute(util.format_query(cr, "CREATE INDEX {} ON {}({})", new_index, table, column))

        util.explode_execute(
            cr,
            util.format_query(
                cr,
                """
                UPDATE {table} t
                   SET {column} = doc.id
                  FROM documents_document doc
                 WHERE t.{column} = doc._upg_old_folder_id
                """,
                table=table,
                column=column,
            ),
            table="documents_document",
            alias="doc",
        )
        cr.execute(
            util.format_query(
                cr,
                """
                DROP INDEX {index_name};

                ALTER TABLE {table}
                ADD FOREIGN KEY ({column}) REFERENCES documents_document(id)
                         ON DELETE {new_action}
                """,
                table=table,
                column=column,
                constraint_name=constraint_name,
                index_name=new_index,
                new_action=sql.SQL(
                    # special case for documents_document: we want SET NULL instead fo RESTRICT
                    "SET NULL" if table == "documents_document" and column == "folder_id" else actions_map[action]
                ),
            )
        )

    cr.execute("ALTER TABLE documents_facet ADD CONSTRAINT documents_facet_name_unique UNIQUE(folder_id, name)")

    # Restore primary keys (also integrity check post re-referencing)
    for m2m in ("documents_folder_read_groups", "documents_folder_res_groups_rel"):
        util.fixup_m2m(cr, m2m, "documents_document", "res_groups", "documents_folder_id", "res_groups_id")

    # replace all remaining references, mostly relevant for indirect references
    cr.execute("SELECT _upg_old_folder_id, id FROM documents_document WHERE _upg_old_folder_id IS NOT NULL")
    folder_mapping = dict(cr.fetchall())
    if folder_mapping:
        util.replace_record_references_batch(cr, folder_mapping, "documents.folder", "documents.document")

    util.merge_model(cr, "documents.folder", "documents.document", drop_table=False, ignore_m2m="*")

    break_recursive_loops(cr, "documents.document", "folder_id")
    cr.execute(  # fix `parent_path`
        """
        WITH RECURSIVE parent_paths AS (
            SELECT id,
                   id::text || '/' AS parent_path
              FROM documents_document
             WHERE type = 'folder'
               AND folder_id is NULL  -- root folders
      UNION SELECT d.id,
                   p.parent_path || d.id || '/' AS parent_path
              FROM documents_document AS d
              JOIN parent_paths AS p
                ON d.folder_id = p.id
    )
    UPDATE documents_document
       SET parent_path = parent_paths.parent_path
      FROM parent_paths
     WHERE parent_paths.id = documents_document.id
    """
    )

    util.create_column(cr, "documents_document", "is_pinned_folder", "boolean", default=False)

    ###################
    # DOCUMENTS.TAGS  #
    ###################

    util.remove_field(cr, "documents.tag", "folder_id")

    # Remove duplicated tags, and keep only one per name, in the English version.
    # Fill a table that will map the removed tag to the one we kept

    # Ensure the xmlids used in the mapping below exist in the database
    # That way the de-duplication keeps those instead since
    # these tag names have many xmlids referencing them in 17.0
    tags_values = {
        "documents_internal_status_inbox": "Inbox",
        "documents_internal_status_tc": "To Validate",
        "documents_internal_status_validated": "Validated",
        "documents_internal_status_deprecated": "Deprecated",
        "documents_finance_documents_bill": "Bill",
        "documents_finance_documents_Contracts": "Contracts",
    }
    for tag_xmlid, tag_name in tags_values.items():
        util.ensure_xmlid_match_record(cr, f"documents.{tag_xmlid}", "documents.tag", {"name": tag_name})
    cr.execute(
        """
        WITH grouped_ids AS (
            SELECT ARRAY_AGG(tag.id ORDER BY
                    imd.module = 'documents' DESC NULLS LAST, -- documents xmlids first
                    imd.name = ANY(%s) DESC NULLS LAST, -- prioritize this set of specific xmlids
                    tag.id ASC
                ) AS ids
              FROM documents_tag AS tag
         LEFT JOIN ir_model_data AS imd
                ON imd.res_id = tag.id
               AND imd.model = 'documents_tag'
          GROUP BY tag.name->'en_US'
        )
        SELECT tag.id, grouped.ids[1]
          FROM documents_tag AS tag
          JOIN grouped_ids AS grouped
            ON tag.id = ANY(grouped.ids)
        """,
        [list(tags_values.keys())],
    )

    tags_mapping = dict(cr.fetchall())
    _tags_mapping = {src: dest for src, dest in tags_mapping.items() if src != dest}
    if _tags_mapping:
        util.replace_record_references_batch(cr, _tags_mapping, "documents.tag", replace_xmlid=True)
        util.remove_records(cr, "documents.tag", list(_tags_mapping))

    # Some tags have been removed because the names were duplicated
    # map the removed tags to new one
    mapping = {
        "documents_internal_status_inbox": "documents_tag_inbox",
        "documents_internal_status_tc": "documents_tag_to_validate",
        "documents_internal_status_validated": "documents_tag_validated",
        "documents_internal_status_deprecated": "documents_tag_deprecated",
        "documents_internal_knowledge_hr": "documents_tag_hr",
        "documents_internal_knowledge_sales": "documents_tag_sales",
        "documents_internal_knowledge_legal": "documents_tag_legal",
        "documents_internal_knowledge_other": "documents_tag_other",
        "documents_internal_template_presentations": "documents_tag_presentations",
        "documents_internal_template_contracts": "documents_tag_contracts",
        "documents_internal_template_project": "documents_tag_project",
        "documents_internal_template_text": "documents_tag_text",
        "documents_finance_status_inbox": "documents_tag_inbox",
        "documents_finance_status_tc": "documents_tag_to_validate",
        "documents_finance_status_validated": "documents_tag_validated",
        "documents_finance_documents_bill": "documents_tag_bill",
        "documents_finance_documents_expense": "documents_tag_expense",
        "documents_finance_documents_vat": "documents_tag_vat",
        "documents_finance_documents_fiscal": "documents_tag_fiscal",
        "documents_finance_documents_financial": "documents_tag_financial",
        "documents_finance_documents_Contracts": "documents_tag_contracts",
        "documents_finance_fiscal_year_2017": "documents_tag_year_previous",
        "documents_finance_fiscal_year_2018": "documents_tag_year_current",
        "documents_marketing_assets_ads": "documents_tag_ads",
        "documents_marketing_assets_brochures": "documents_tag_brochures",
        "documents_marketing_assets_images": "documents_tag_images",
        "documents_marketing_assets_Videos": "documents_tag_videos",
    }

    for old_name, new_name in mapping.items():
        # rename the first element
        util.rename_xmlid(cr, f"documents.{old_name}", f"documents.{new_name}", on_collision="merge")
    # Try to steal the tag from documents_project if available.
    util.rename_xmlid(cr, "documents_project.documents_project_status_draft", "documents.documents_tag_draft")

    cr.execute("ALTER TABLE documents_tag ALTER COLUMN facet_id DROP NOT NULL")

    ####################
    # DOCUMENTS.ACCESS #
    ####################

    cr.execute(
        """
        CREATE TABLE documents_access (
            id SERIAL PRIMARY KEY,
            create_uid integer,
            create_date timestamp without time zone,
            write_uid integer,
            write_date timestamp without time zone,
            document_id integer,
            partner_id integer,
            role varchar,
            expiration_date timestamp without time zone,
            -- is the access created because of a group (other than internal)
            _upg_added_from_group boolean
        )
        """
    )
    cr.execute(
        """
        ALTER TABLE documents_access
        ADD CONSTRAINT unique_document_access_partner
        unique(document_id, partner_id)
        """
    )

    # Folders without group: access_internal == 'edit'
    # Folders without groups (read&write) or with internal user group (read): access_internal == 'view'
    cr.execute(
        """
        UPDATE documents_document
           SET access_internal = CASE
                   WHEN (read_group IS NULL AND (write_group IS NULL OR write_group.res_groups_id = %(internal)s))
                   THEN 'edit'
                   WHEN (((read_group IS NULL AND write_group IS NULL) OR read_group.res_groups_id = %(internal)s))
                   THEN 'view'
                   ELSE NULL
               END
          FROM documents_document AS folder
     LEFT JOIN documents_folder_read_groups AS read_group
            ON folder.id = read_group.documents_folder_id
     LEFT JOIN documents_folder_res_groups_rel AS write_group
            ON folder.id = write_group.documents_folder_id
         WHERE documents_document.id = folder.id
           AND documents_document.access_internal IS NULL
           AND folder.type = 'folder'
        """,
        {"internal": internal_id},
    )

    # Propagate access_internal from the folder to the documents inside of if
    # (but not on the folders inside of it)
    util.explode_execute(
        cr,
        """
        UPDATE documents_document document
           SET access_internal = folder.access_internal
          FROM documents_document AS folder
         WHERE folder.id = document.folder_id
           AND document.type != 'folder'
           AND {parallel_filter}
        """,
        table="documents_document",
        alias="document",
    )

    # For each non-internal groups, create one <documents.access> per user in the group on the folder
    # if he's in the company
    cr.execute(
        """
       INSERT INTO documents_access (document_id, partner_id, role, _upg_added_from_group) (
            SELECT folder.id,
                   res_users.partner_id,
                   'edit',
                   TRUE
              FROM documents_document AS folder
              JOIN documents_folder_res_groups_rel AS write_group
                ON folder.id = write_group.documents_folder_id
              JOIN res_groups_users_rel AS group_rel
                ON group_rel.gid = write_group.res_groups_id
               AND group_rel.gid != %(internal)s
         LEFT JOIN res_company_users_rel AS comp_rel
                ON comp_rel.user_id = group_rel.uid
               AND comp_rel.cid = folder.company_id
              JOIN res_users
                ON res_users.id = group_rel.uid
               AND res_users.active
             WHERE folder.type = 'folder'
               AND (folder.company_id IS NULL OR comp_rel.cid IS NOT NULL)
        )
                ON CONFLICT DO NOTHING
        """,
        {"internal": internal_id},
    )

    cr.execute(
        """
       INSERT INTO documents_access (document_id, partner_id, role, _upg_added_from_group) (
            SELECT folder.id,
                   res_users.partner_id,
                   'view',
                   TRUE
              FROM documents_document AS folder
              JOIN documents_folder_read_groups AS read_group
                ON folder.id = read_group.documents_folder_id
              JOIN res_groups_users_rel AS group_rel
                ON group_rel.gid = read_group.res_groups_id
               AND group_rel.gid != %(internal)s
         LEFT JOIN res_company_users_rel AS comp_rel
                ON comp_rel.user_id = group_rel.uid
               AND comp_rel.cid = folder.company_id
              JOIN res_users
                ON res_users.id = group_rel.uid
               AND res_users.active
             WHERE folder.type = 'folder'
               AND (folder.company_id IS NULL OR comp_rel.cid IS NOT NULL)
        )
                ON CONFLICT DO NOTHING
        """,
        {"internal": internal_id},
    )

    # Check that large groups mitigation was unnecessary or done correctly
    check_or_raise_many_members(cr)

    # Copy the <documents.access> of the folders, on the direct documents inside of it
    cr.execute(
        """
       INSERT INTO documents_access (document_id, partner_id, role, _upg_added_from_group) (
            SELECT document.id,
                   access.partner_id,
                   access.role,
                   TRUE
              FROM documents_document AS folder
              JOIN documents_folder AS old_folder
                ON old_folder.id = folder._upg_old_folder_id
              JOIN documents_access AS access
                ON access.document_id = folder.id
              JOIN documents_document AS document
                ON document.folder_id = folder.id
               AND document.type != 'folder'
             WHERE folder.type = 'folder'
               AND CASE access.role
                     WHEN 'view' THEN old_folder.user_specific IS NOT TRUE
                     WHEN 'edit' THEN old_folder.user_specific_write IS NOT TRUE
                     ELSE false
                   END
        )
        """,
    )

    ###########################################
    # DOCUMENTS.ACCESS - user_specific_folder #
    ###########################################

    # Create a <documents.access> for the owner of the file, then
    # remove the owner of the file otherwise he will get write access

    # For user_specific_write, we can just keep the owner of the file

    user_specific_folder = """
        WITH user_specific_folder AS (
             SELECT folder.id AS id,
                    user_specific_write IS TRUE AS write,
                    folder.company_id
               FROM documents_folder AS old_folder
               JOIN documents_document AS folder
                 ON old_folder.id = folder._upg_old_folder_id
              WHERE (old_folder.user_specific OR old_folder.user_specific_write)
                AND {parallel_filter}
        )
    """

    util.explode_execute(
        cr,
        user_specific_folder
        + """
           INSERT INTO documents_access (document_id, partner_id, role, _upg_added_from_group) (
                SELECT document.id,
                       u.partner_id,
                       'view',
                       FALSE
                  FROM user_specific_folder AS folder
                  JOIN documents_document AS document
                    ON document.folder_id = folder.id

                    -- owner needs the group to be added as viewer
                  JOIN documents_folder_read_groups AS read_group
                    ON folder.id = read_group.documents_folder_id
                  JOIN res_groups_users_rel AS group_rel
                    ON group_rel.gid = read_group.res_groups_id

                    -- owner needs to be in the company
             LEFT JOIN res_company_users_rel AS comp_rel
                    ON comp_rel.user_id = group_rel.uid
                   AND comp_rel.cid = folder.company_id

                  JOIN res_users AS u
                    ON u.id = document.owner_id
                   AND group_rel.uid = u.id

                 WHERE NOT folder.write
                   AND (folder.company_id IS NULL OR comp_rel.cid IS NOT NULL)
              GROUP BY document.id, u.partner_id
            )
                ON CONFLICT (document_id, partner_id)  -- maybe has write access from group_ids
                DO UPDATE SET _upg_added_from_group = FALSE
            """,
        table="documents_folder",
        alias="old_folder",
    )

    util.explode_execute(
        cr,
        cr.mogrify(
            user_specific_folder
            + """
            UPDATE documents_document d
               SET access_internal = CASE
                       WHEN d.type != 'folder' THEN 'none'
                       ELSE d.access_internal
                   END,
                   is_access_via_link_hidden = TRUE,
                   -- Remove the owner for user_specific == TRUE - user_specific_write = FALSE
                   -- Or if the user is not in the "write group" / in the folder company
                   owner_id = CASE WHEN (
                       NOT folder.write
                        OR group_rel IS NULL
                        OR (folder.company_id is NOT NULL AND comp_rel.cid IS NULL)
                   ) THEN %s ELSE d.owner_id END,
                   -- Set the contact if we reset the owner and if the contact is false
                   partner_id = CASE
                       WHEN (
                           NOT folder.write
                           OR group_rel IS NULL
                           OR (folder.company_id is NOT NULL AND comp_rel.cid IS NULL)
                       ) AND d.partner_id IS NULL THEN usr.partner_id
                       ELSE d.partner_id
                   END
              FROM documents_document AS doc
              JOIN user_specific_folder AS folder
                ON doc.folder_id = folder.id

         LEFT JOIN res_users AS usr
                ON usr.id = doc.owner_id

                   -- is the owner in the "write group" ?
         LEFT JOIN documents_folder_res_groups_rel AS write_group
                ON folder.id = write_group.documents_folder_id
         LEFT JOIN res_groups_users_rel AS group_rel
                ON group_rel.gid = write_group.res_groups_id
               AND group_rel.uid = doc.owner_id

                   -- owner need to be in the company
         LEFT JOIN res_company_users_rel AS comp_rel
                ON comp_rel.user_id = group_rel.uid
               AND comp_rel.cid = folder.company_id

             WHERE doc.id = d.id
            """,
            [util.ref(cr, "base.user_root")],
        ).decode(),
        table="documents_folder",
        alias="old_folder",
    )

    # For the folders (not the files), which are user specific,
    # - set access_internal = 'none' if all user can see it, but not write inside of it
    # - remove the members with only read access (only keep those who can write in the folder)
    # (because new files created inside of it will inherit from the folder access, and
    # we don't want them to be accessible by default)
    util.explode_execute(
        cr,
        cr.mogrify(
            user_specific_folder
            + """
            UPDATE documents_document d
               SET access_internal = 'none'
              FROM user_specific_folder AS folder
         LEFT JOIN documents_folder_res_groups_rel AS write_group
                ON folder.id = write_group.documents_folder_id
             WHERE d.id = folder.id
               AND access_internal = 'view'
               AND (write_group IS NULL OR write_group.res_groups_id != %(internal)s)
            """,
            {"internal": internal_id},
        ).decode(),
        table="documents_folder",
        alias="old_folder",
    )
    util.explode_execute(
        cr,
        user_specific_folder
        + """
            DELETE
              FROM documents_access a
             USING user_specific_folder u
             WHERE a.document_id = u.id
               AND a.role = 'view'
               AND a._upg_added_from_group IS TRUE
        """,
        table="documents_folder",
        alias="old_folder",
    )

    # For the special case of the user_specific_write folders on the root, with group=internal,
    # we keep access_internal=edit, because users won't be able to write on the folder
    # itself, because it's pinned, but so they can still upload in it after the migration
    # Done here to not propagate the access on the documents inside of it
    util.explode_execute(
        cr,
        cr.mogrify(
            """
            UPDATE documents_document d
               SET access_internal = 'edit'
              FROM documents_document AS folder
              JOIN documents_folder AS old_folder
                ON old_folder._upg_new_folder_id = folder.id
               AND old_folder.user_specific_write IS TRUE
              JOIN documents_folder_res_groups_rel AS write_group
                ON write_group.documents_folder_id = folder.id
               AND write_group.res_groups_id = %(internal)s
             WHERE d.id = folder.id
               AND d.folder_id IS NULL
            """,
            {"internal": internal_id},
        ).decode(),
        table="documents_document",
        alias="folder",
    )

    ###################
    # DOCUMENTS.SHARE #
    ###################
    # remove non-indexed FK to accelerate the deletion.
    # (this is not an issue as the model, and its FKs, will be removed anyway)
    for table, column, constraint_name, _action in util.get_fk(cr, "documents_share", quote_ident=False):
        if not util.get_index_on(cr, table, column):
            cr.execute(util.format_query(cr, "ALTER TABLE {} DROP CONSTRAINT {}", table, constraint_name))

    # Remove all shares with an expiration date, because we don't support that feature
    # anymore (and we don't want to extend the access the user had)
    util.explode_execute(cr, "DELETE FROM documents_share WHERE date_deadline IS NOT NULL", table="documents_share")

    # When migrating the shares, because we will do a stupid redirection,
    # we can not keep access_via_link == edit (otherwise the read share will gain write access)
    # so we do the simplest solution and we force `access_via_link == view` everywhere
    cr.execute(
        """
        CREATE TABLE documents_redirect (
            id SERIAL PRIMARY KEY,
            create_uid INTEGER,
            create_date TIMESTAMP WITHOUT TIME ZONE,
            write_uid INTEGER,
            write_date TIMESTAMP WITHOUT TIME ZONE,
            document_id INTEGER,
            access_token VARCHAR
        )
        """
    )

    # We don't migrate non-"include sub-folder" shares, shares of selected documents ids, or shares
    # with a customized domain.
    # But we might need the share for the sub-modules migration, so we add a new column
    # to flag the share that we want to ignore here
    util.create_column(cr, "documents_share", "to_ignore", "boolean")
    util.explode_execute(
        cr,
        r"""
        UPDATE documents_share
           SET to_ignore = TRUE
         WHERE TYPE = 'domain'
           AND (NOT include_sub_folders
                OR regexp_replace(domain, '[\s\[\]()''"]+', '', 'g') != 'folder_id,child_of,' || folder_id)
           AND {parallel_filter}
        """,
        table="documents_share",
        alias="documents_share",
    )

    # Share folders
    util.explode_execute(
        cr,
        """
     INSERT INTO documents_redirect (document_id, access_token)
          SELECT document.id,
                 share.access_token
            FROM documents_share AS share
            JOIN documents_document AS document
              ON document._upg_old_folder_id = share.folder_id
           WHERE share.type = 'domain'
             AND share.to_ignore = FALSE
             AND {parallel_filter}
         """,
        table="documents_share",
        alias="share",
    )

    # Insert redirect token for shares used in only one document
    util.explode_execute(
        cr,
        """
        WITH shares AS (
              SELECT share.access_token AS access_token,
                     min(rel.documents_document_id) AS document_id
                FROM documents_share AS share
                JOIN documents_document_documents_share_rel AS rel
                  ON share.id = rel.documents_share_id
               WHERE share.to_ignore = FALSE
                 AND share.type = 'ids'
                 AND {parallel_filter}
            GROUP BY share.id
              HAVING COUNT(rel.documents_document_id) = 1
        )
     INSERT INTO documents_redirect (document_id, access_token)
          SELECT share.document_id,
                 share.access_token
            FROM shares AS share
        """,
        table="documents_share",
        alias="share",
    )

    # Force access_via_link == 'view' on all documents that have a non-ignored share
    # (with is_access_via_link_hidden=TRUE if no access_internal so that sharing does not make it accessible through discovery)
    # or were included in (is_access_via_link_hidden=FALSE or shared folders would seem empty)
    # We have to do two passes to make sure to make the first level of a migrated share
    # discoverable if it is included in another share.

    util.explode_execute(
        cr,
        """
         UPDATE documents_document d
            SET access_via_link = 'view',
                is_access_via_link_hidden = (COALESCE(d.access_internal, 'none') = 'none'),
                _upg_was_shared = TRUE
           FROM documents_redirect AS redirect
          WHERE d.id = redirect.document_id
            AND {parallel_filter}
        """,
        table="documents_document",
        alias="d",
    )
    util.explode_execute(
        cr,
        """
         UPDATE documents_document d
            SET access_via_link = 'view',
                _upg_was_shared = TRUE
           FROM documents_redirect AS redirect
           JOIN documents_document doc
             ON doc.id = redirect.document_id
          WHERE d.parent_path like doc.parent_path || '_%' -- only children
            AND {parallel_filter}
        """,
        table="documents_document",
        alias="d",
    )

    ##############
    # MAIL.ALIAS #
    ##############

    document_model_id = util.ref(cr, "documents.model_documents_document")
    share_model_id = util.ref(cr, "documents.model_documents_share")
    util.remove_constraint(cr, "documents_share", "documents_share_alias_id_fkey")

    # Remove all alias names if email_drop = FALSE
    # (to disable an alias, we just remove the alias_name now)
    cr.execute(
        """
        UPDATE mail_alias
           SET alias_name = NULL
          FROM documents_share
         WHERE NOT email_drop
           AND documents_share.alias_id = mail_alias.id
           AND mail_alias.alias_model_id = %(document_model_id)s
           AND documents_share.to_ignore = FALSE
        """,
        {"document_model_id": document_model_id},
    )

    # Set one mail alias per document, in priority the one that has tags
    # Other aliases will still exist, but we won't be able to change the
    # tags in the documents UI
    util.explode_execute(
        cr,
        cr.mogrify(
            """
        WITH main_alias AS (  -- the alias that will be set on <documents.document>
    SELECT DISTINCT ON (document.id)
                       alias.id AS id,
                       document.id AS document_id
                  FROM mail_alias AS alias
                  JOIN documents_share AS share
                    ON share.alias_id =  alias.id
                   AND share.to_ignore = FALSE
                  JOIN documents_document AS document
                    ON document._upg_old_folder_id = share.folder_id
             LEFT JOIN documents_share_documents_tag_rel AS tag_rel
                    ON tag_rel.documents_share_id = share.id
                 WHERE alias_model_id = %s
                   AND alias_name IS NOT NULL
                   AND {parallel_filter}
                   -- shares with tag have the priority (then most recent share)
              ORDER BY document.id, (tag_rel IS NULL), share.id DESC
        )
        UPDATE documents_document
           SET alias_id = alias.id
          FROM main_alias AS alias
         WHERE documents_document.id = alias.document_id
            """,
            [document_model_id],
        ).decode(),
        table="documents_document",
        alias="document",
    )

    # Fix `alias_parent_model_id` and `alias_parent_thread_id`
    util.explode_execute(
        cr,
        cr.mogrify(
            """
                 UPDATE mail_alias
                    SET alias_parent_model_id = %(document_model_id)s,
                        alias_parent_thread_id = document.id
                   FROM documents_share AS share
                   JOIN documents_document AS document
                     ON document._upg_old_folder_id = share.folder_id
                  WHERE alias_model_id = %(document_model_id)s
                    AND alias_parent_model_id = %(share_model_id)s
                    AND share.alias_id = mail_alias.id
                    AND share.to_ignore = FALSE
                    AND {parallel_filter}
                """,
            {"document_model_id": document_model_id, "share_model_id": share_model_id},
        ).decode(),
        table="documents_share",
        alias="share",
    )

    # Migrate the main alias (the one that will be on the document)
    util.explode_execute(
        cr,
        """
         UPDATE documents_document
            SET create_activity_option = share.activity_option,
                create_activity_type_id = share.activity_type_id,
                create_activity_summary = share.activity_summary,
                create_activity_date_deadline_range = share.activity_date_deadline_range,
                create_activity_date_deadline_range_type = share.activity_date_deadline_range_type,
                create_activity_note = share.activity_note,
                create_activity_user_id = share.activity_user_id
           FROM documents_share AS share
          WHERE share.alias_id = documents_document.alias_id
            AND share.to_ignore = FALSE
            AND {parallel_filter}
        """,
        table="documents_share",
        alias="share",
    )

    cr.execute(
        """
        CREATE TABLE document_alias_tag_rel (
            documents_document_id integer,
            documents_tag_id integer,
            PRIMARY KEY (documents_document_id, documents_tag_id)
        )
        """
    )

    cr.execute(
        r"""
        SELECT document.id AS document_id,
               alias.id AS alias_id,
               alias.alias_defaults
          FROM mail_alias AS alias
     LEFT JOIN documents_document AS document
            ON document.alias_id = alias.id
         WHERE alias_model_id = %(document_model_id)s
           AND alias_defaults IS NOT NULL
           -- will be done in python, limit as much as possible the number of records
           AND alias_defaults ILIKE '%%tag\_ids%%'
        """,
        {"document_model_id": document_model_id},
    )

    for r in cr.dictfetchall():
        alias_id = r["alias_id"]
        document_id = r["document_id"]  # if document is set, it's the main alias
        defaults = ast.literal_eval(r["alias_defaults"])

        tags = defaults.get("tag_ids")
        if not tags:
            continue

        if tags and isinstance(tags[0], int):  # [1, 2, 3]
            pass
        elif len(tags) == 1 and len(tags[0]) == 3 and tags[0][0] == 6:  # [[6, 0, [1, 2, 3]]]
            tags = tags[0][2]
        elif all(len(t) >= 2 and t[0] == 4 for t in tags):  # [[4, 1], [4, 2], [4, 3]]
            tags = [t[1] for t in tags]
        else:
            tags = []  # do not migrate other commands TODO: decide about reporting to users

        tags = list({tags_mapping[t] for t in tags if t in tags_mapping})

        if document_id:  # first alias values are migrated on the documents
            cr.execute(
                """
             INSERT INTO document_alias_tag_rel (documents_document_id, documents_tag_id) (
                  SELECT document.id,
                         tag.id
                    FROM documents_document AS document
                    JOIN documents_tag AS tag
                      ON tag.id = ANY(%(tags)s) -- check existence and remove duplicated
                   WHERE document.id = %(document_id)s
               )
                 ON CONFLICT DO NOTHING
                """,
                {"document_id": document_id, "tags": tags},
            )

            # Now that the tags are on the <documents.document>, we need to remove them from alias_id
            # The other aliases will keep `tag_ids` in `alias_defaults`
            del defaults["tag_ids"]

        # others are kept in the alias
        elif tags:
            defaults["tag_ids"] = [[6, 0, tags]]
        else:
            del defaults["tag_ids"]

        cr.execute(
            """
         UPDATE mail_alias
            SET alias_defaults = %(alias_defaults)s
          WHERE id = %(alias_id)s
            """,
            {"alias_id": alias_id, "alias_defaults": str(defaults)},
        )

    # Update the `folder_id` key in `alias_defaults`
    query = cr.mogrify(
        r"""
        WITH cte AS (
            SELECT id,
                   substring(alias_defaults FROM '["'']folder_id["'']:\s*([0-9]+)')::int AS _upg_old_folder_id
              FROM mail_alias
             WHERE alias_model_id = %s
               AND {parallel_filter}
        )
        UPDATE mail_alias a
           SET alias_defaults = REGEXP_REPLACE(
                   alias_defaults,
                   '(["''])folder_id\1:\s*' || document._upg_old_folder_id,
                   '\1folder_id\1: ' || document.id
               )
          FROM documents_document AS document
          JOIN cte
            ON cte._upg_old_folder_id = document._upg_old_folder_id
         WHERE a.id = cte.id
        """,
        [document_model_id],
    ).decode()
    util.explode_execute(cr, query, table="mail_alias")

    # Update alias_defaults for creating activity on secondary alias
    # Note that the document created with the alias_defaults is used as a template for creating all the document for all the
    # mail attachment. We take advantage of that here by setting the create_xx field that will be used to create the activities
    # on the final document. If those create_xx fields are set, they take precedence over the create_xx of the folder.
    cr.execute(
        """
    SELECT alias.id AS alias_id,
           alias.alias_defaults,
           share.activity_type_id,
           share.activity_summary,
           share.activity_note,
           share.activity_user_id,
           share.activity_date_deadline_range,
           share.activity_date_deadline_range_type
      FROM mail_alias as alias
      JOIN documents_share as share
        ON share.alias_id = alias.id
 LEFT JOIN documents_document doc
        ON doc.alias_id = alias.id
     WHERE doc IS NULL
       AND share.activity_option
       AND share.to_ignore = FALSE
        """
    )
    alias_update_queries = []
    for r in cr.dictfetchall():
        try:
            alias_defaults = ast.literal_eval(r["alias_defaults"])
        except ValueError:
            continue  # Ignore malformed alias_defaults
        create_data = {
            f"create_{field_name}": r[field_name]
            for field_name in (
                "activity_type_id",
                "activity_summary",
                "activity_note",
                "activity_user_id",
                "activity_date_deadline_range",
                "activity_date_deadline_range_type",
            )
            if r[field_name]
        }
        if create_data:
            alias_defaults["create_activity_option"] = True
            alias_defaults.update(create_data)
            alias_update_queries.append(
                cr.mogrify(
                    "UPDATE mail_alias SET alias_defaults = %s WHERE id = %s", [repr(alias_defaults), r["alias_id"]]
                )
            )
    util.parallel_execute(cr, alias_update_queries)

    # Create an alias for the other documents (column is required)
    fix_missing_alias_ids(cr, document_model_id=document_model_id)

    #########################
    # PROPAGATE THE COMPANY #
    #########################

    # As users could nest folders accessible to other companies, propagate the company
    # from the parent to the immediate non-folder children only

    util.explode_execute(
        cr,
        """
        WITH folders_with_company AS (
            SELECT id, company_id
              FROM documents_document
             WHERE type = 'folder'
               AND company_id IS NOT NULL
        )
        UPDATE documents_document d
           SET company_id = f.company_id
          FROM folders_with_company f
         WHERE d.folder_id = f.id
           AND d.type != 'folder'
           AND d.company_id IS NULL
           AND {parallel_filter}
        """,
        table="documents_document",
        alias="d",
    )

    ################################
    # FIX THE MISSING ACCESS TOKEN #
    ################################

    fix_missing_document_tokens(cr)

    ###################
    # ADD FOREIGN KEY #
    ###################

    cr.execute(
        """
        ALTER TABLE documents_document
        ADD FOREIGN KEY ("alias_id")
        REFERENCES "mail_alias"("id")
        ON DELETE restrict
        """
    )

    #####################
    # MIGRATE THE XMLID #
    #####################

    xmlid_mapping = {
        "documents_internal_folder": "document_internal_folder",
        "documents_finance_folder": "document_finance_folder",
        "documents_marketing_folder": "document_marketing_folder",
        "documents_marketing_brand1_folder": "document_marketing_brand1_folder",
        "documents_marketing_brand2_folder": "document_marketing_brand2_folder",
    }

    migrate_folders_xmlid(cr, "documents", xmlid_mapping)

    #########
    # Views #
    #########
    util.remove_view(cr, "documents.share_view_form_popup")
    util.remove_view(cr, "documents.share_view_form")
    util.remove_view(cr, "documents.share_view_tree")
    util.remove_view(cr, "documents.share_view_search")
    util.remove_view(cr, "documents.share_files_page")
    util.remove_view(cr, "documents.share_workspace_page")
    util.remove_view(cr, "documents.workflow_rule_form_view")
    util.remove_view(cr, "documents.workflow_rule_view_tree")
    util.remove_view(cr, "documents.action_view_search")
    util.remove_view(cr, "documents.workflow_action_view_form")
    util.remove_view(cr, "documents.workflow_action_view_tree")
    util.remove_record(cr, "documents.documents_kanban_view_mobile_scss")
    util.remove_view(cr, "documents.folder_view_form")
    util.remove_view(cr, "documents.folder_view_tree")
    util.remove_view(cr, "documents.folder_view_search")


def migrate_folders_xmlid(cr, module, xmlid_mapping):
    for old_name, new_name in xmlid_mapping.items():
        util.rename_xmlid(cr, f"{module}.{old_name}", f"{module}.{new_name}")


def fix_missing_alias_ids(cr, document_model_id=False):
    if not document_model_id:
        document_model_id = util.ref(cr, "documents.model_documents_document")

    util.explode_execute(
        cr,
        cr.mogrify(
            """
            WITH _aliases AS (
                INSERT INTO mail_alias (alias_name,
                                        alias_model_id, alias_parent_model_id,
                                        alias_parent_thread_id, alias_force_thread_id,
                                        alias_defaults,
                                        alias_contact, alias_status)
                     SELECT NULL,
                            %s, %s,
                            d.id, d.id,
                            jsonb_build_object('folder_id', d.id)::text,
                            'followers', 'invalid'
                       FROM documents_document d
                      WHERE d.alias_id IS NULL
                        AND {parallel_filter}
                  RETURNING id, alias_force_thread_id)
            UPDATE documents_document d
               SET alias_id = a.id
              FROM _aliases a
             WHERE a.alias_force_thread_id = d.id
            """,
            [document_model_id, document_model_id],
        ).decode(),
        table="documents_document",
        alias="d",
    )


def fix_missing_document_tokens(cr):
    """Fill the empty `document_token` column of the `documents_document` table."""
    cr.execute("SELECT 1 FROM pg_proc WHERE proname = 'gen_random_bytes'")
    if not cr.fetchall():
        BATCH = 1000
        ncr = util.named_cursor(cr, BATCH)
        ncr.execute(
            """
            SELECT id
              FROM documents_document
             WHERE document_token IS NULL
            """
        )

        res = ncr.fetchmany(BATCH)
        upd_query = "UPDATE documents_document SET document_token = (%s::jsonb->>id::text)::text WHERE id IN %s"
        while res:
            data = {r[0]: base64.urlsafe_b64encode(uuid.uuid4().bytes).decode().removesuffix("==") for r in res}
            cr.execute(upd_query, [psycopg2.extras.Json(data), tuple(data)])
            res = ncr.fetchmany(BATCH)
        ncr.close()
    else:
        # pgsql 13
        cr.execute(
            """
             UPDATE documents_document
                SET document_token = REPLACE(REPLACE(REPLACE(encode(gen_random_bytes(16), 'base64'), '=', ''), '+', '-'), '/', '_')
              WHERE document_token IS NULL
            """
        )


def check_or_raise_large_groups(cr, internal_id):
    large_groups_option = getenv("ODOO_UPG_18_DOCUMENTS_FOLDERS_LARGE_GROUPS_RIGHTS")
    if large_groups_option and large_groups_option not in DOCUMENTS_FOLDERS_LARGE_GROUPS_RIGHTS_OPTIONS:
        raise util.MigrationError("Documents: Incorrect value for ODOO_UPG_18_DOCUMENTS_FOLDERS_LARGE_GROUPS_RIGHTS.")
    if large_groups_option == "ACCEPT_AS_IS":
        return

    cr.execute(
        """
        WITH groups_company_users AS (
            SELECT gu.gid AS gid,
                   gu.uid AS uid,
                   cu.cid AS cid
              FROM res_groups_users_rel gu
              JOIN res_company_users_rel cu
                ON cu.user_id = gu.uid
             WHERE gu.gid <> %(internal)s

         UNION ALL

            SELECT gid,
                   uid,
                   NULL::int4 AS cid
              FROM res_groups_users_rel
             WHERE gid <> %(internal)s
        ),
        -- Get all non-user-specific groups for each folder
        folders_groups_kind AS (
            SELECT rg.documents_folder_id AS fid,
                   rg.res_groups_id AS gid,
                   'READ' AS kind
              FROM documents_folder_read_groups rg
              JOIN documents_folder f
                ON f.id = rg.documents_folder_id
               AND f.user_specific IS NOT TRUE
             WHERE rg.res_groups_id <> %(internal)s

         UNION ALL

             SELECT wg.documents_folder_id AS fid,
                    wg.res_groups_id AS gid,
                    'WRITE' AS kind
              FROM documents_folder_res_groups_rel wg
              JOIN documents_folder f
                ON f.id = wg.documents_folder_id
               AND f.user_specific_write IS NOT TRUE
             WHERE res_groups_id <> %(internal)s
        ),
        -- Get unique groups for each folder
        folders_unique_groups AS (
            SELECT fid,
                   gid
              FROM folders_groups_kind
          GROUP BY fid, gid
        ),
        -- Identify folders with too many unique active allowed users across groups
        many_users_folders AS (
            SELECT f.id AS fid,
                   f.name as fname,
                   c.name as cname,
                   COUNT(DISTINCT gcu.uid) AS total_users
              FROM documents_folder f
         LEFT JOIN res_company c
                ON c.id = f.company_id
              JOIN folders_unique_groups fug
                ON fug.fid = f.id
              JOIN groups_company_users gcu
                ON gcu.gid = fug.gid
               AND gcu.cid IS NOT DISTINCT FROM f.company_id
              JOIN res_users u
                ON u.id = gcu.uid
               AND u.active
          GROUP BY f.id, f.name, c.name
            HAVING COUNT(DISTINCT gcu.uid) > %(max_members)s
        )
        -- Retrieve groups info
        SELECT muf.fid AS folder_id,
               muf.fname->>'en_US',
               muf.cname,
               muf.total_users,
               JSONB_AGG(JSONB_BUILD_OBJECT(
                    'kind', fgk.kind,
                    'name', g.name->>'en_US',
                    'id', fgk.gid
               ))
          FROM many_users_folders muf
          JOIN folders_groups_kind fgk
            ON muf.fid = fgk.fid
          JOIN res_groups g
            ON fgk.gid = g.id
      GROUP BY muf.fid, muf.fname->>'en_US', muf.cname, muf.total_users
      ORDER BY muf.total_users DESC
    """,
        {"max_members": FOLDERS_GROUPS_MAX_MEMBERS, "internal": internal_id},
    )
    folders_groups_data = cr.fetchall()

    if not folders_groups_data:
        return
    many_members_folder_ids = [folder_data[0] for folder_data in folders_groups_data]

    if large_groups_option == "SET_NOBODY":
        # replace large groups with temporary empty group
        group_nobody_id = util.ENVIRON["documents_group_nobody_id"] = (
            util.env(cr)["res.groups"].create({"name": "_UPG_NOBODY"}).id
        )
        cr.execute(
            """
            WITH _rm AS (
               DELETE
                 FROM documents_folder_read_groups r
                WHERE documents_folder_id = ANY(%(large_read)s)
            RETURNING documents_folder_id
            )
         INSERT INTO documents_folder_read_groups(documents_folder_id, res_groups_id)
              SELECT documents_folder_id, %(group_nobody)s
                FROM _rm
            GROUP BY documents_folder_id
        """,
            {"group_nobody": group_nobody_id, "large_read": many_members_folder_ids},
        )
        cr.execute(
            """
            WITH _rm AS (
               DELETE
                 FROM documents_folder_res_groups_rel r
                WHERE documents_folder_id = ANY(%(large_write)s)
            RETURNING documents_folder_id
            )
     INSERT INTO documents_folder_res_groups_rel(documents_folder_id, res_groups_id)
          SELECT documents_folder_id, %(group_nobody)s
            FROM _rm
        GROUP BY documents_folder_id
        """,
            {"group_nobody": group_nobody_id, "large_write": many_members_folder_ids},
        )
        return

    if large_groups_option == "SET_USER_SPECIFIC":
        execute_values(
            cr._obj,
            """
            UPDATE documents_folder f
               SET user_specific = TRUE,
                   user_specific_write = TRUE
              FROM (VALUES %s) AS fus (folder_id)
             WHERE fus.folder_id = f.id
        """,
            [(folder_id,) for folder_id in many_members_folder_ids],
        )
        return

    # Otherwise, prepare helpful error message
    workspaces_users_report_lines = []
    for folder_id, folder_name, company_name, folder_users, folder_groups in folders_groups_data:
        kinds_groups = defaultdict(list)
        for group in folder_groups:
            kinds_groups[group["kind"]].append((group["id"], group["name"]))
        folder_kind_groups = []
        for kind, kind_groups in kinds_groups.items():
            groups_list = ", ".join(f'"{group_name}" (id={group_id})' for group_id, group_name in kind_groups)
            folder_kind_groups.append(f"    * {kind}: {groups_list}")
        kind_groups_message = "\n".join(folder_kind_groups)
        workspaces_users_report_lines.append(
            f'- [{int(folder_users)} users]: "{folder_name}" (id={folder_id}, company={company_name}) '
            f"with groups:\n{kind_groups_message}"
        )
    workspaces_users_report = "\n".join(workspaces_users_report_lines)

    raise util.MigrationError(f"""
Many-member groups used on Documents Workspaces:

{workspaces_users_report}

Upgrading as-is would have two downsides:
    1. The access rights panel could get *very* hard to manage (adding or removing members among a large list)
    2. The Documents application can become slow to use

Several options are available, possibly in combination:

    1. Adapting your configuration:
      * If restricting is not that important, remove the group configuration on the folder
      * If restricting is important:
        * Use another group with fewer members instead / reduce the number of members of the group
        * Set the group as user-specific (read/write) so users keep access to their own documents only

    2. Ask Odoo Support to enable one of the following settings (this can be done after 1 too) using
      the ODOO_UPG_18_DOCUMENTS_FOLDERS_LARGE_GROUPS_RIGHTS key with the following possible values:
      * SET_USER_SPECIFIC: Set these folders groups configuration as USER_SPECIFIC for READ AND WRITE automatically
      * SET_NOBODY: Set these folders as restricted access, only users with the new Documents group
        "System Administrator" will be able to view and edit these folders (including access rights)
        after the upgrade.
      * ACCEPT_AS_IS: Confirm that the current configuration is what you need and upgrade as-is.
""")


def check_or_raise_many_members(cr):
    large_groups_option = getenv("ODOO_UPG_18_DOCUMENTS_FOLDERS_LARGE_GROUPS_RIGHTS")
    if large_groups_option == "ACCEPT_AS_IS":
        return

    cr.execute(
        """
        SELECT COUNT(*)
          FROM documents_access
      GROUP BY document_id
        HAVING COUNT(*) > %(max_members)s
        """,
        {"max_members": FOLDERS_GROUPS_MAX_MEMBERS},
    )
    if cr.fetchall():
        if large_groups_option:
            raise util.MigrationError("Documents: Failure to mitigate large number of members.")
        raise util.MigrationError("Documents: unexpectedly large number of members to be created.")


@contextlib.contextmanager
def create_documents_fix_token_and_alias(cr):
    """Create documents and fix document_token and alias_id (for folders) columns."""

    cr.execute("ALTER TABLE documents_document ALTER COLUMN document_token DROP NOT NULL")

    try:
        yield

    finally:
        document_model_id = util.ref(cr, "documents.model_documents_document")

        util.explode_execute(
            cr,
            cr.mogrify(
                """
                WITH _aliases AS (
                    INSERT INTO mail_alias (alias_name,
                                            alias_model_id, alias_parent_model_id,
                                            alias_parent_thread_id, alias_force_thread_id,
                                            alias_defaults,
                                            alias_contact, alias_status)
                         SELECT NULL,
                                %s, %s,
                                d.id, d.id,
                                jsonb_build_object('folder_id', d.id)::text,
                                'followers', 'invalid'
                           FROM documents_document d
                          WHERE d.alias_id IS NULL
                            AND type = 'folder'
                            AND {parallel_filter}
                      RETURNING id, alias_force_thread_id)
                UPDATE documents_document d
                   SET alias_id = a.id
                  FROM _aliases a
                 WHERE a.alias_force_thread_id = d.id
                """,
                [document_model_id, document_model_id],
            ).decode(),
            table="documents_document",
            alias="d",
        )

        fix_missing_document_tokens(cr)
        cr.execute("ALTER TABLE documents_document ALTER COLUMN document_token SET NOT NULL")
