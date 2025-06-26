from odoo.upgrade import util

documents_18_pre_migrate = util.import_script("documents/saas~17.5.1.4/pre-migrate.py")


def migrate(cr, version):
    # Create inbox folder
    activity_todo_id = util.ref(cr, "mail.mail_activity_data_todo")
    user_root_id = util.ref(cr, "base.user_root")

    # Create inbox folder
    cr.execute("ALTER TABLE documents_document ALTER COLUMN document_token DROP NOT NULL")
    cr.execute(
        """
        INSERT INTO documents_document (
            name, company_id, "type",
            folder_id, owner_id, active,
            access_internal, access_via_link,
            create_activity_type_id, create_activity_user_id
        ) VALUES (
            JSONB_BUILD_OBJECT('en_US', 'Inbox'), NULL, 'folder',
            NULL, NULL, TRUE,
            'edit', 'none',
            %s, %s
        )
        RETURNING id
    """,
        [activity_todo_id, user_root_id],
    )
    inbox_folder_id = cr.fetchone()[0]
    documents_18_pre_migrate.fix_missing_document_tokens(cr)

    cr.execute(
        """
        INSERT INTO ir_model_data(name, module, model, res_id, noupdate)
        VALUES ('document_inbox_folder', 'documents', 'documents.document', %s, true)
        """,
        [inbox_folder_id],
    )

    # If "inbox" alias already exists, create xml_id for it so that a new record (data) is not created.
    cr.execute("SELECT id FROM mail_alias WHERE alias_name='inbox'")
    if cr.rowcount:
        alias_id = cr.fetchone()[0]
        cr.execute(
            """
            INSERT INTO ir_model_data(name, module, model, res_id, noupdate)
                 VALUES ('document_inbox_folder_mail_alias', 'documents', 'mail.alias', %s, true)
            """,
            [alias_id],
        )

    util.remove_model(cr, "documents.access.invite")


def wrap_documents_server_action(cr, xmlid, suffix="_code"):
    """Create a "multi" server action to wrap an action as child with the provided suffix.

    Does nothing if xmlid is not found.
    """
    existing_action_id = util.rename_xmlid(cr, xmlid, f"{xmlid}{suffix}")
    if not existing_action_id:
        return
    cr.execute(
        """
        INSERT INTO ir_act_server (name, model_id, state, type, usage, binding_type)
             SELECT name, model_id, 'multi', type, usage, 'action'
               FROM ir_act_server
              WHERE id = %s
          RETURNING id
        """,
        [existing_action_id],
    )
    multi_action_id = cr.fetchone()[0]
    cr.execute("UPDATE ir_act_server SET parent_id = %s WHERE id = %s", [multi_action_id, existing_action_id])
    cr.execute(
        """
        INSERT INTO ir_act_server_group_rel(act_id, gid)
             SELECT %s, gid
               FROM ir_act_server_group_rel
              WHERE act_id = %s
        """,
        [multi_action_id, existing_action_id],
    )
    cr.execute(
        "UPDATE ir_embedded_actions SET action_id = %s WHERE action_id = %s", [multi_action_id, existing_action_id]
    )

    util.ensure_xmlid_match_record(cr, xmlid, "ir.actions.server", {"id": multi_action_id})
