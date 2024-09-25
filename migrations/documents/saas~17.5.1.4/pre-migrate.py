import ast
import base64
import uuid

import psycopg2

from odoo.upgrade import util
from odoo.upgrade.util.inconsistencies import break_recursive_loops


def migrate(cr, version):
    #####################
    # DOCUMENTS.FOLDERS #
    #####################

    util.remove_constraint(  # the model changed
        cr,
        "documents_document",
        "documents_document_folder_id_fkey",
    )
    cr.execute("ALTER TABLE documents_document ALTER COLUMN folder_id DROP NOT NULL")

    # create a temporary column to store the old <documents.folder>.id
    util.create_column(cr, "documents_document", "_upg_old_folder_id", "int4")

    # new <documents.document> fields
    util.create_column(cr, "documents_document", "is_access_via_link_hidden", "boolean")
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

    cr.execute(
        """
    INSERT INTO documents_document (
                    _upg_old_folder_id, name, type, res_id, res_model,
                    active, parent_path, company_id, folder_id
                ) (
         SELECT id,
                name->>'en_US',  -- <documents.folder>.name is translatable,
                                 -- <documents.document>.name is not
                'folder',
                NULL,
                NULL,
                active,
                NULL, -- to be set for all documents
                company_id,
                parent_folder_id
           FROM documents_folder
    )
        """
    )

    update_m2o_documents_folder(cr, "documents_document", "folder_id")

    cr.execute(
        """
         ALTER TABLE documents_document
      ADD CONSTRAINT fk_folder_id FOREIGN KEY (folder_id)
          REFERENCES documents_document(id)
        """
    )

    break_recursive_loops(cr, "documents.document", "folder_id")
    cr.execute(  # fix `parent_path`
        """
        WITH RECURSIVE parent_paths AS (
            SELECT id,
                   folder_id,
                   id::text || '/' AS parent_path
              FROM documents_document
             WHERE type = 'folder'
               AND folder_id is NULL  -- root folders
      UNION SELECT d.id,
                   d.folder_id,
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

    ###################
    # DOCUMENTS.TAGS  #
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

    # Remove duplicated tags, and keep only one per name, in the English version.
    # Fill a table that will map the removed tag to the one we kept
    cr.execute(
        """
        WITH grouped_ids AS (
            SELECT ARRAY_AGG(id ORDER BY id ASC) AS ids
              FROM documents_tag
          GROUP BY name->'en_US'
        )
        SELECT tag.id, grouped.ids[1]
          FROM documents_tag AS tag
          JOIN grouped_ids AS grouped
           ON tag.id = ANY(grouped.ids)
        """
    )
    tags_mapping = dict(cr.fetchall())
    _tags_mapping = {src: dest for src, dest in tags_mapping.items() if src != dest}
    util.replace_record_references_batch(cr, _tags_mapping, "documents.tag", replace_xmlid=False)
    cr.execute("DELETE FROM documents_tag WHERE id = ANY(%s)", [list(_tags_mapping)])

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
        "documents_finance_documents_bill": "documents_tag_bill",
        "documents_finance_documents_expense": "documents_tag_expense",
        "documents_finance_documents_vat": "documents_tag_vat",
        "documents_finance_documents_fiscal": "documents_tag_fiscal",
        "documents_finance_documents_financial": "documents_tag_financial",
        "documents_finance_fiscal_year_2017": "documents_tag_year_previous",
        "documents_finance_fiscal_year_2018": "documents_tag_year_current",
        "documents_marketing_assets_ads": "documents_tag_ads",
        "documents_marketing_assets_brochures": "documents_tag_brochures",
        "documents_marketing_assets_images": "documents_tag_images",
        "documents_marketing_assets_Videos": "documents_tag_videos",
    }

    for old_name, new_name in mapping.items():
        # rename the first element
        util.rename_xmlid(cr, f"documents.{old_name}", f"documents.{new_name}")

    ####################
    # DOCUMENTS.ACCESS #
    ####################

    internal_id = util.ref(cr, "base.group_user")

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
            -- temporary column, true if the user is in read_group
            _upg_is_read_group_set boolean
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
            ON folder._upg_old_folder_id = read_group.documents_folder_id
     LEFT JOIN documents_folder_res_groups_rel AS write_group
            ON folder._upg_old_folder_id = write_group.documents_folder_id
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
    cr.execute(
        """
       INSERT INTO documents_access (document_id, partner_id, role) (
            SELECT folder.id,
                   res_users.partner_id,
                   'edit'
              FROM documents_document AS folder
              JOIN documents_folder_res_groups_rel AS write_group
                ON folder._upg_old_folder_id = write_group.documents_folder_id
              JOIN res_groups_users_rel AS rel
                ON rel.gid = write_group.res_groups_id
               AND rel.gid != %(internal)s
              JOIN res_users
                ON res_users.id = rel.uid
               AND res_users.active
             WHERE folder.type = 'folder'
        )
                ON CONFLICT DO NOTHING
        """,
        {"internal": internal_id},
    )

    cr.execute(
        """
       INSERT INTO documents_access (document_id, partner_id, role, _upg_is_read_group_set) (
            SELECT folder.id,
                   res_users.partner_id,
                   'view',
                   TRUE
              FROM documents_document AS folder
              JOIN documents_folder_read_groups AS read_group
                ON folder._upg_old_folder_id = read_group.documents_folder_id
              JOIN res_groups_users_rel AS rel
                ON rel.gid = read_group.res_groups_id
               AND rel.gid != %(internal)s
              JOIN res_users
                ON res_users.id = rel.uid
               AND res_users.active
             WHERE folder.type = 'folder'
        )
                ON CONFLICT (document_id, partner_id)
                DO UPDATE SET _upg_is_read_group_set = TRUE
        """,
        {"internal": internal_id},
    )

    # Copy the <documents.access> of the folders, on the direct documents inside of it
    cr.execute(
        """
       INSERT INTO documents_access (document_id, partner_id, role) (
            SELECT document.id,
                   access.partner_id,
                   -- if we were in the write group AND in the read group,
                   -- we only gain read access on the file
                   'view'
              FROM documents_document AS folder
              JOIN documents_access AS access
                ON access.document_id = folder.id
               AND _upg_is_read_group_set -- only the read group should be propagated
              JOIN documents_document AS document
                ON document.folder_id = folder.id
               AND document.type != 'folder'
             WHERE folder.type = 'folder'
        )
                ON CONFLICT DO NOTHING
        """,
    )

    util.remove_column(cr, "documents_access", "_upg_is_read_group_set")

    ###########################################
    # DOCUMENTS.ACCESS - user_specific_folder #
    ###########################################

    # Create a <documents.access> for the owner of the file, then
    # remove the owner of the file otherwise he will get write access

    # For user_specific_write, we can just keep the owner of the file

    user_specific_folder = """
        WITH user_specific_folder AS (
             SELECT folder.id AS id,
                    COALESCE(user_specific_write, FALSE) AS write
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
           INSERT INTO documents_access (document_id, partner_id, role) (
                SELECT document.id,
                       u.partner_id,
                       'view'
                  FROM user_specific_folder AS folder
                  JOIN documents_document AS document
                    ON document.folder_id = folder.id
                  JOIN res_users AS u
                    ON u.id = document.owner_id
                 WHERE NOT folder.write
            )
                ON CONFLICT DO NOTHING -- maybe has write access from group_ids
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
                   owner_id = CASE WHEN NOT folder.write THEN %s ELSE d.owner_id END
              FROM user_specific_folder AS folder
             WHERE d.folder_id = folder.id
            """,
            [util.ref(cr, "base.user_root")],
        ).decode(),
        table="documents_folder",
        alias="old_folder",
    )

    ###################
    # DOCUMENTS.SHARE #
    ###################

    # Remove all shares with an expiration date, because we don't support that feature
    # anymore (and we don't want to extend the access the user had)
    cr.execute("DELETE FROM documents_share WHERE date_deadline IS NOT NULL")

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
          SELECT convert_id.id,
                 share.access_token
            FROM documents_share AS share
            JOIN documents_document AS convert_id
              ON convert_id._upg_old_folder_id = share.folder_id
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

    # Force access_via_link == 'view' on all documents that had a share
    util.explode_execute(
        cr,
        """
         UPDATE documents_document
            SET access_via_link = 'view'
           FROM documents_redirect AS redirect
          WHERE redirect.document_id = documents_document.id
            AND {parallel_filter}
        """,
        table="documents_document",
        alias="documents_document",
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
    cr.execute(
        r"""
         UPDATE mail_alias
            SET alias_defaults = REGEXP_REPLACE(
                    alias_defaults,
                    '''folder_id'':\s*([0-9]+)',
                    '''folder_id'': ' || document.id
                )
           FROM documents_document AS document
          WHERE alias_model_id = %(document_model_id)s
            AND alias_defaults ~ ('''folder_id'':\s*' || (document._upg_old_folder_id::text) || '\D')
        """,
        {"document_model_id": document_model_id},
    )

    # Update alias_defaults for creating activity on secondary alias
    # Note that the document created with the alias_defaults is used as a template for creating all the document for all the
    # mail attachment. We take advantage of that here by setting the create_xx field that will be used to create the activities
    # on the final document. If those create_xx fields are set, they take precedence over the create_xx of the folder.
    cr.execute(
        r"""
    WITH share AS (
        SELECT alias_id,
               $$'create_activity_option': True$$ ||
                COALESCE($$, 'create_activity_type_id': $$ || activity_type_id, '') ||
                COALESCE($$, 'create_activity_summary': '$$ || activity_summary || $$'$$, '') ||
                COALESCE($$, 'create_activity_note': '$$ || activity_note || $$'$$, '') ||
                COALESCE($$, 'create_activity_user_id': $$ || activity_user_id, '') ||
                COALESCE($$, 'create_activity_date_deadline_range': $$ || activity_date_deadline_range, '') ||
                COALESCE($$, 'create_activity_date_deadline_range_type': '$$ || activity_date_deadline_range_type || $$'$$, '')
                AS create_activity_data
          FROM documents_share
          WHERE alias_id NOT IN (SELECT alias_id FROM documents_document WHERE alias_id IS NOT NULL)
            AND activity_option IS TRUE
            AND documents_share.to_ignore = FALSE
    )
     UPDATE mail_alias
        SET alias_defaults = CASE
          WHEN alias_defaults ~ '^\s*{\s*}\s*$' THEN '{' || share.create_activity_data || '}'
          ELSE regexp_replace(alias_defaults, '\s*}\s*$', ', ' || share.create_activity_data || '}')
        END
       FROM share
      WHERE id = share.alias_id
        AND alias_defaults NOT LIKE '%activity_ids%'
        """
    )

    #########################
    # PROPAGATE THE COMPANY #
    #########################

    # Propagate the company from the parent to the children
    # For that, we look for the first folder in the ancestors with a company
    # In that example, C and D will get the company 2
    # A (company 1)
    # |
    # B (company 2)
    # |
    # C (no company)
    # |
    # D (no company)
    break_recursive_loops(cr, "documents.document", "folder_id")
    cr.execute(
        """
WITH RECURSIVE docs AS (
            -- start from all documents that have company set
            -- and at least one child with NULL company
        SELECT p.id,
               p.company_id
          FROM documents_document p
          JOIN documents_document c
            ON c.folder_id = p.id
         WHERE p.company_id IS NOT NULL
           AND c.company_id IS NULL
      GROUP BY p.id

         UNION ALL -- fine to use ALL because we always add new ids
            -- propagate the company from parent to child
            -- when child has NULL company
        SELECT c.id,
               p.company_id
          FROM documents_document c
          JOIN docs p
            ON p.id = c.folder_id
         WHERE c.company_id IS NULL
    )
            -- update only the documents that have NULL company
        UPDATE documents_document d
           SET company_id = docs.company_id
          FROM docs
         WHERE d.id = docs.id
           AND d.company_id IS NULL
        """
    )

    ################################
    # FIX THE MISSING ACCESS TOKEN #
    ################################

    fix_missing_document_tokens(cr)

    ############################################
    # RE-MAP documents.folder relational field #
    ############################################
    for table, column, constraint_name, delete_action in util.get_fk(cr, "documents_folder"):
        other_columns = util.get_columns(cr, table, ignore=(column,))
        if len(other_columns) == 1:  # m2m
            continue
        util.remove_constraint(cr, table, constraint_name)
        update_m2o_documents_folder(cr, table, column)

        _delete_action = {
            "a": "NO ACTION",
            "r": "RESTRICT",
            "c": "CASCADE",
            "n": "SET NULL",
            "d": "SET DEFAULT",
        }[delete_action]

        query = util.format_query(
            cr,
            """
            ALTER TABLE {table}
            ADD FOREIGN KEY ({column})
            REFERENCES "documents_document"("id")
            ON DELETE {delete_action}
            """,
            table=table,
            column=column,
            delete_action=psycopg2.sql.SQL(_delete_action),
        )
        cr.execute(query)

    ###################
    # ADD FOREIGN KEY #
    ###################

    cr.execute(
        """
        ALTER TABLE documents_document
        ADD FOREIGN KEY ("folder_id")
        REFERENCES "documents_document"("id")
        ON DELETE set null
        """
    )

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
    util.remove_view(cr, "documents.facet_view_tree")
    util.remove_view(cr, "documents.facet_view_form_with_folder")
    util.remove_view(cr, "documents.facet_view_form")
    util.remove_view(cr, "documents.facet_view_search")
    util.remove_view(cr, "documents.share_files_page")
    util.remove_view(cr, "documents.share_workspace_page")
    util.remove_view(cr, "documents.workflow_rule_form_view")
    util.remove_view(cr, "documents.workflow_rule_view_tree")
    util.remove_view(cr, "documents.action_view_search")
    util.remove_view(cr, "documents.workflow_action_view_form")
    util.remove_view(cr, "documents.workflow_action_view_tree")
    util.remove_record(cr, "documents.documents_kanban_view_mobile_scss")


def update_m2o_documents_folder(cr, table, field):
    """Update the many2one from <documents.folder> to <documents.document>"""
    query = util.format_query(
        cr,
        """
        UPDATE {table}
           SET {field} = folder.id
          FROM documents_document AS folder
         WHERE folder.type = 'folder'
           AND folder._upg_old_folder_id = {table}.{field}
        """,
        table=table,
        field=field,
    )
    cr.execute(query)


def migrate_folders_xmlid(cr, module, xmlid_mapping):
    for old_name, new_name in xmlid_mapping.items():
        cr.execute(
            """
                UPDATE ir_model_data AS imd
                  SET res_id = d.id, model = 'documents.document'
                 FROM documents_document d
                WHERE imd.module = %s
                  AND imd.model = 'documents.folder'
                  AND imd.name = %s
                  AND d._upg_old_folder_id = imd.res_id
            """,
            [module, old_name],
        )
        util.rename_xmlid(cr, f"{module}.{old_name}", f"{module}.{new_name}")


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
        upd_query = "UPDATE documents_document SET document_token = (%s::jsonb->id::text)::text WHERE id IN %s"
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
