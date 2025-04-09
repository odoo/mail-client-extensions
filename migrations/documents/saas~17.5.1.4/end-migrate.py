import re
from collections import defaultdict
from itertools import chain, cycle

from psycopg2 import sql

from odoo.upgrade import util


def migrate(cr, version):
    #################
    # DOCUMENTS.TAG #
    #################

    ############
    # OWNER ID #
    ############

    # Reset the owner, if the user didn't have write access
    # (at the very end, because spreadsheet creates records)
    util.explode_execute(
        cr,
        cr.mogrify(
            """
                UPDATE documents_document
                   SET owner_id = %s,
                       partner_id = COALESCE(document.partner_id, usr.partner_id)
                  FROM documents_document AS document
                  JOIN res_users AS usr
                    ON usr.id = document.owner_id
             LEFT JOIN documents_access AS access
                    ON access.document_id = document.id
                   AND access.role = 'edit'
                   AND access.partner_id = usr.partner_id
             LEFT JOIN documents_folder f
                    ON f._upg_new_folder_id = document.folder_id
                 WHERE document.access_internal IS DISTINCT FROM 'edit'
                   AND access IS NULL
                   AND documents_document.id = document.id
                   AND NOT COALESCE(f.user_specific, FALSE)
                   AND NOT COALESCE(f.user_specific_write, FALSE)
                   AND {parallel_filter}
            """,
            [util.ref(cr, "base.user_root")],
        ).decode(),
        table="documents_document",
        alias="document",
    )

    ##########################
    # MIGRATE WORKFLOW RULES #
    ##########################
    util.create_column(cr, "ir_act_server", "_upg_name", "varchar")
    cr.execute("CREATE UNIQUE INDEX on ir_act_server(_upg_name)")
    documents_tag_model_id = util.ref(cr, "documents.model_documents_document_tag")
    documents_action_id = util.ref(cr, "documents.document_action")
    cr.execute("SELECT id FROM ir_model_fields WHERE model='documents.document' AND name='tag_ids'")
    documents_tag_ids_field_id = cr.fetchone()[0]
    cr.execute("SELECT id, name->>'en_US' FROM mail_activity_type")
    activity_type_name_by_id = dict(cr.fetchall())
    document_model_id = util.ref(cr, "documents.model_documents_document")
    internal_id = util.ref(cr, "base.group_user")
    init_existing_server_act = [
        "ir_actions_server_remove_activities",
        "ir_actions_server_tag_remove_inbox",
        "ir_actions_server_tag_remove_to_validate",
        "ir_actions_server_tag_add_validated",
        "ir_actions_server_tag_add_bill",
    ]
    existing_server_act = set(init_existing_server_act)
    cr.execute(
        """
        UPDATE ir_act_server a
           SET _upg_name = d.name
          FROM ir_model_data d
         WHERE d.res_id = a.id
           AND d.model = 'ir.actions.server'
           AND d.module = 'documents'
           AND d.name IN %s
        """,
        [tuple(existing_server_act)],
    )
    cr.execute(
        """
        SELECT documents_workflow_rule_id,
               ARRAY_AGG(documents_tag_id)
          FROM required_tag_ids_rule_table
      GROUP BY documents_workflow_rule_id
        """
    )
    required_tag_ids_by_workflow_rule = dict(cr.fetchall())
    cr.execute(
        """
        SELECT documents_workflow_rule_id,
               ARRAY_AGG(documents_tag_id)
          FROM excluded_tag_ids_rule_table
      GROUP BY documents_workflow_rule_id
        """
    )
    excluded_tag_ids_by_workflow_rule = dict(cr.fetchall())
    cr.execute("CREATE SEQUENCE _upg_document_sequence_action")
    queries_steps = migrate_workflow_rule(
        cr=cr,
        document_model_id=document_model_id,
        documents_action_id=documents_action_id,
        internal_id=internal_id,
        documents_tag_model=documents_tag_model_id,
        documents_tag_ids_field=documents_tag_ids_field_id,
        activity_type_name_by_id=activity_type_name_by_id,
        existing_server_act=existing_server_act,
        required_tag_ids_by_workflow_rule=required_tag_ids_by_workflow_rule,
        excluded_tag_ids_by_workflow_rule=excluded_tag_ids_by_workflow_rule,
    )
    for queries in queries_steps:
        util.parallel_execute(cr, queries)
    cr.execute("DROP SEQUENCE _upg_document_sequence_action")
    cr.execute(
        "SELECT id FROM ir_act_server WHERE _upg_name IS NOT NULL AND _upg_name NOT IN %s",
        [tuple(init_existing_server_act)],
    )
    if new_action_ids := [tuple_id[0] for tuple_id in cr.fetchall()]:
        util.recompute_fields(
            cr,
            "ir.actions.server",
            (
                "crud_model_id",
                "link_field_id",
                "update_field_id",
                "update_related_model_id",
                # mail
                "template_id",
                "mail_post_autofollow",
                "mail_post_method",
                "activity_summary",
                "activity_note",
                "activity_date_deadline_range",
                "activity_date_deadline_range_type",
                "activity_user_type",
                "activity_user_id",
                "activity_user_field_name",
            ),
            ids=new_action_ids,
        )
        # migrated to code server actions should be excluded from the cloc for maintenance fees
        cr.execute(
            """
            INSERT INTO ir_model_data (name, module, model, res_id, noupdate)
                 SELECT 'document_workflow_migrated_to_server_action_' || id,
                        '__cloc_exclude__',
                        'ir.actions.server',
                        id,
                        TRUE
                   FROM ir_act_server
                  WHERE id = ANY(%s)
                    AND state = 'code'
            """,
            [new_action_ids],
        )

    ############
    # CLEAN DB #
    ############
    # we might need those field for the sub-modules migration
    util.remove_column(cr, "documents_document", "_upg_old_folder_id")
    util.remove_column(cr, "documents_document", "_upg_was_shared")
    util.remove_field(cr, "documents.document", "group_ids")
    util.remove_field(cr, "documents.document", "available_rule_ids")
    util.remove_field(cr, "documents.document", "is_shared")

    util.remove_column(cr, "documents_access", "_upg_added_from_group")

    util.remove_model(cr, "documents.folder")
    util.remove_model(cr, "documents.share")

    util.remove_model(cr, "documents.workflow.rule")
    util.remove_model(cr, "documents.workflow.action")

    util.remove_field(cr, "documents.tag", "facet_id")
    util.remove_model(cr, "documents.facet")

    util.remove_column(cr, "ir_act_server", "_upg_name")

    if gid := util.ENVIRON.get("documents_group_nobody_id"):
        util.remove_record(cr, ("res.groups", gid))

    ###############
    # ACCESS.RULE #
    ###############
    util.remove_record(cr, "documents.documents_folder_global_rule")
    util.remove_record(cr, "documents.documents_folder_groups_rule")
    util.remove_record(cr, "documents.documents_folder_manager_rule")

    util.remove_record(cr, "documents.documents_document_readonly_rule")
    util.remove_record(cr, "documents.documents_document_write_rule")
    util.remove_record(cr, "documents.documents_document_manager_rule")
    util.update_record_from_xml(cr, "documents.documents_document_global_rule")
    util.update_record_from_xml(cr, "documents.documents_document_global_write_rule")
    util.update_record_from_xml(cr, "documents.documents_access_global_rule_read")
    util.update_record_from_xml(cr, "documents.documents_access_global_rule_write")
    util.update_record_from_xml(cr, "documents.mail_plan_rule_group_document_manager_document")
    util.update_record_from_xml(cr, "documents.mail_plan_template_rule_group_document_manager_document")
    util.update_record_from_xml(cr, "documents.documents_tag_rule_portal")

    ##################
    # PINNED FOLDERS #
    ##################

    # Pin odoobot folders at the company root, so users are not lost
    util.explode_execute(
        cr,
        cr.mogrify(
            """
                UPDATE documents_document
                   SET is_pinned_folder = TRUE
                  FROM documents_document document
                 WHERE documents_document.id = document.id
                   AND document.type='folder'
                   AND document.folder_id IS NULL
                   AND document.owner_id = %s
                   AND {parallel_filter}
            """,
            [util.ref(cr, "base.user_root")],
        ).decode(),
        table="documents_document",
        alias="document",
    )


def build_insert_ir_act_server(
    cr,
    internal_id,
    model_id,
    name,
    upg_name,
    sequence,
    state,
    code=None,
    update_field_id=None,
    update_related_model_id=None,
    selection_value=None,
    update_path=None,
    update_m2m_operation=None,
    update_boolean_value=None,
    evaluation_type=None,
    resource_ref=None,
    value=None,
    crud_model_id=None,
    activity_type_id=None,
    activity_summary=None,
    activity_date_deadline_range=None,
    activity_date_deadline_range_type=None,
    activity_note=None,
    activity_user_type=None,
    activity_user_field_name=None,
    activity_user_id=None,
    child_names=None,
):
    extra_values_with_defaults = {
        "mail_post_autofollow": False,
        "code": code if code else "",
        "update_field_id": update_field_id,
        "update_related_model_id": update_related_model_id,
        "selection_value": selection_value,
        "update_path": update_path,
        "update_m2m_operation": update_m2m_operation if update_m2m_operation else "add",
        "update_boolean_value": update_boolean_value if update_boolean_value else "true",
        "evaluation_type": evaluation_type if evaluation_type else "value",
        "resource_ref": resource_ref,
        "value": value,
        "crud_model_id": crud_model_id,
        "activity_type_id": activity_type_id,
        "activity_summary": activity_summary,
        "activity_date_deadline_range": activity_date_deadline_range if activity_date_deadline_range else 0,
        "activity_date_deadline_range_type": activity_date_deadline_range_type,
        "activity_note": activity_note,
        "activity_user_type": activity_user_type,
        "activity_user_field_name": activity_user_field_name,
        "activity_user_id": activity_user_id,
    }
    keys = list(extra_values_with_defaults.keys())
    insert_children = (
        """
        INSERT INTO rel_server_actions("server_id", "action_id")
             SELECT inserted_act.act_id, child_action.id
               FROM inserted_act
               JOIN ir_act_server AS child_action
                 ON child_action._upg_name = ANY(%s)
        """
        if child_names
        else None
    )

    query = util.format_query(
        cr,
        """
        WITH inserted_act AS (
            INSERT INTO ir_act_server(
                "create_uid",
                "create_date",
                "write_uid",
                "write_date",
                "type",
                "binding_type",
                "usage",
                "binding_view_types",
                "model_name",
                "name",
                "model_id",
                "_upg_name",
                "sequence",
                "state",
                {extra_columns}
            )
            VALUES(
                1, -- create_uid
                now() at time zone 'utc', --create_date
                1, -- write_uid
                now() at time zone 'utc', -- write_date
                'ir.actions.server', -- type
                'action', -- binding_type
                'ir_actions_server', -- usage
                'list,form', -- binding_view_types
                'documents.document', -- model_name
                jsonb_build_object('en_US', %s), -- name
                %s, -- model_id
                %s, -- _upg_name
                %s, -- sequence
                %s, -- state
                {extra_values}
            )
            RETURNING id as act_id
        )
        {insert_children}
        INSERT INTO ir_act_server_group_rel("act_id", "gid")
             SELECT act_id, %s
               FROM inserted_act
        """,
        extra_columns=sql.SQL(", ").join(map(sql.Identifier, keys)),
        extra_values=sql.SQL(", ".join(["%s"] * len(keys))),
        insert_children=sql.SQL(f", _ AS ({insert_children})" if child_names else ""),
    )
    values = (
        [name, model_id, upg_name, sequence, state]
        + [extra_values_with_defaults[k] for k in keys]
        + ([child_names] if child_names else [])
        + [internal_id]  # for insert into query ir_act_server_group_rel
    )
    return cr.mogrify(query, values)


def sanitize(str_value):
    return re.sub("([^a-z0-9_]+)", "_", str_value.lower())


def groupby(iterable, key):
    groups = defaultdict(list)
    for elem in iterable:
        groups[key(elem)].append(elem)
    return groups.items()


def migrate_workflow_rule(
    cr,
    document_model_id,
    documents_action_id,
    internal_id,
    documents_tag_model,
    documents_tag_ids_field,
    activity_type_name_by_id,
    existing_server_act,
    required_tag_ids_by_workflow_rule,
    excluded_tag_ids_by_workflow_rule,
):
    cr.execute(
        """
        SELECT wr.id, wr.name, wr.partner_id, wr.user_id, wr.folder_id, wr.remove_activities,
               wr.activity_option, wr.activity_type_id, wr.activity_summary, wr.activity_date_deadline_range,
               wr.activity_date_deadline_range_type, wr.activity_note, wr.has_owner_activity, wr.activity_user_id,
               wr.domain_folder_id, wr.create_model, wr.link_model,
               wr.condition_type, wr.criteria_partner_id, wr.criteria_owner_id, wr.domain
          FROM documents_workflow_rule wr
     LEFT JOIN ir_model_data imd
            ON imd.res_id = wr.id
           AND imd.model = 'documents.workflow.rule'
         WHERE imd.id IS NULL;
        """
    )
    workflow_rules = cr.dictfetchall()

    if not workflow_rules:
        return [], [], []

    cr.execute("SELECT id, model FROM ir_model")
    model_by_id = {row["id"]: row["model"] for row in cr.dictfetchall()}
    journal_by_workflow_rule_id = {}
    if util.module_installed(cr, "documents_account"):
        cr.execute("SELECT id FROM ir_model_fields WHERE name = 'journal_id' AND model = 'documents.workflow.rule'")
        journal_id_field = cr.fetchone()
        if journal_id_field:
            journal_id_field = journal_id_field[0]
            cr.execute("SELECT res_id, value_reference FROM _ir_property WHERE fields_id = %s;", (journal_id_field,))
            journal_by_workflow_rule_id = {
                int(record["res_id"].split(",")[1]): int(record["value_reference"].split(",")[1])
                for record in cr.dictfetchall()
                if record["value_reference"]
            }
    method_by_create_model = {
        "hr.expense": ("document_hr_expense_create_hr_expense", []),
        "hr.applicant": ("document_hr_recruitment_create_hr_candidate", []),
        "product.template": ("create_product_template", []),
        "project.task": ("action_create_project_task", []),
        "sign.template.new": ("document_sign_create_sign_template_x", ["'sign.template.new'"]),
        "sign.template.direct": ("document_sign_create_sign_template_x", ["'sign.template.direct'"]),
        "account.move.in_invoice": ("account_create_account_move", ["'in_invoice'"]),
        "account.move.out_invoice": ("account_create_account_move", ["'out_invoice'"]),
        "account.move.in_refund": ("account_create_account_move", ["'in_refund'"]),
        "account.move.out_refund": ("account_create_account_move", ["'out_refund'"]),
        "account.move.entry": ("account_create_account_move", ["'entry'"]),
        "account.bank.statement": ("account_create_account_bank_statement", []),
        "account.move.in_receipt": ("account_create_account_move", ["'in_receipt'"]),
    }
    cr.execute(
        """
        SELECT wr.id AS wr_id,
               act.action,
               act.facet_id,
               act.tag_id
          FROM documents_workflow_rule wr
          JOIN documents_workflow_action act
            ON act.workflow_rule_id = wr.id
          JOIN documents_tag tag
            ON tag.id = act.tag_id
         WHERE wr.id IN %s
        """,
        [tuple(wr["id"] for wr in workflow_rules)],
    )
    workflow_actions = dict(groupby(cr.dictfetchall(), lambda r: r["wr_id"]))
    cr.execute(
        """
        SELECT tag.id,
               tag.name->>'en_US' AS name,
               tag.facet_id
          FROM documents_tag tag
        """
    )
    tag_info = {r["id"]: r for r in cr.dictfetchall()}
    tags_by_facet = {
        grouped_key: [grouped_value["id"] for grouped_value in grouped_values]
        for grouped_key, grouped_values in groupby(tag_info.values(), lambda r: r["facet_id"])
    }
    all_tag_ids_remove = set()
    all_tag_ids_add = set()
    server_actions = []
    queries_step_1 = []
    for workflow_rule in workflow_rules:
        workflow_rule_id = workflow_rule["id"]
        workflow_rule_name = workflow_rule["name"]["en_US"]
        code = []
        children = []
        values_to_set = {
            field: workflow_rule[column_name]
            for column_name, field in (
                ("partner_id", "partner_id"),
                ("user_id", "owner_id"),
            )
            if workflow_rule[column_name]
        }
        if values_to_set:
            code.append(f"records.write({values_to_set!r})")

        if tags_modifiers := workflow_actions.get(workflow_rule_id):
            tag_ids_to_remove = set()
            tag_ids_to_add = set()
            for tag_modifier in tags_modifiers:
                action = tag_modifier["action"]
                tag_id = tag_modifier["tag_id"]
                if action == "replace":
                    tag_ids_to_remove.update(tags_by_facet.get(tag_modifier.get("facet_id"), []))
                if action in ("replace", "add") and tag_id:
                    tag_ids_to_add.add(tag_id)
                elif action == "remove" and tag_id:
                    tag_ids_to_remove.add(tag_id)
            tag_ids_to_remove.difference_update(tag_ids_to_add)
            all_tag_ids_remove.update(tag_ids_to_remove)
            all_tag_ids_add.update(tag_ids_to_add)
            children += [
                f"ir_actions_server_tag_add_{sanitize(tag_info[tag_id]['name'])}_{tag_info[tag_id]}"
                for tag_id in tag_ids_to_add
            ] + [
                f"ir_actions_server_tag_remove_{sanitize(tag_info[tag_id]['name'])}_{tag_info[tag_id]}"
                for tag_id in tag_ids_to_remove
            ]

        if workflow_rule["remove_activities"]:
            children.append("ir_actions_server_remove_activities")

        if workflow_rule["folder_id"]:
            code.append(f"records.action_move_documents({int(workflow_rule['folder_id'])})")

        if workflow_rule["activity_option"] and workflow_rule["activity_type_id"]:
            activity_type_name = activity_type_name_by_id[workflow_rule["activity_type_id"]]
            name = f"Create Activity {activity_type_name}"
            upg_name = f"{workflow_rule['id']}_{name}"
            queries_step_1.append(
                build_insert_ir_act_server(
                    cr=cr,
                    internal_id=internal_id,
                    model_id=document_model_id,
                    name=name,
                    upg_name=upg_name,
                    sequence=15,
                    state="next_activity",
                    activity_type_id=workflow_rule["activity_type_id"],
                    activity_summary=workflow_rule["activity_summary"],
                    activity_date_deadline_range=max(0, workflow_rule["activity_date_deadline_range"] or 0),
                    activity_date_deadline_range_type=workflow_rule["activity_date_deadline_range_type"],
                    activity_note=workflow_rule["activity_note"],
                    activity_user_type="generic" if workflow_rule["has_owner_activity"] else "specific",
                    activity_user_field_name="owner_id" if workflow_rule["has_owner_activity"] else None,
                    activity_user_id=None if workflow_rule["has_owner_activity"] else workflow_rule["activity_user_id"],
                )
            )
            children.append(upg_name)

        create_model = workflow_rule["create_model"]
        if create_model == "link.to.record":
            link_model = workflow_rule["link_model"]
            model_name = model_by_id[link_model] if link_model else ""
            name = f"ir_actions_server_link_to_{sanitize(model_name)}" if model_name else "ir_actions_server_link_to"
            upg_name = name
            if upg_name not in existing_server_act:
                queries_step_1.append(
                    build_insert_ir_act_server(
                        cr=cr,
                        internal_id=internal_id,
                        model_id=document_model_id,
                        name=name,
                        upg_name=upg_name,
                        sequence=100,
                        state="code",
                        code=f"""action = records.action_link_to_record({model_name!r})"""
                        if model_name
                        else """action = records.action_link_to_record()""",
                    )
                )
            existing_server_act.add(upg_name)
            children.append(upg_name)
        elif create_model in method_by_create_model:
            method_name, parameters = method_by_create_model[create_model]
            if create_model.startswith("account.") and (
                journal_id := journal_by_workflow_rule_id.get(workflow_rule_id)
            ):
                parameters = [*parameters, str(journal_id)]
            name = f"ir_actions_server_{method_name}"
            if parameters:
                name += "_" + ("_".join([p.replace("'", "") for p in parameters]))
            method_call = f"{method_name}({','.join(parameters)})"
            upg_name = name
            if upg_name not in existing_server_act:
                queries_step_1.append(
                    build_insert_ir_act_server(
                        cr=cr,
                        internal_id=internal_id,
                        model_id=document_model_id,
                        name=name,
                        upg_name=upg_name,
                        sequence=100,
                        state="code",
                        code=f"""action = records.{method_call}""",
                    )
                )
            existing_server_act.add(upg_name)
            children.append(upg_name)

        # computed field overridden by documents_sign
        limited_to_single_record = workflow_rule["create_model"] == "sign.template.direct"
        has_criterion = bool(
            limited_to_single_record
            or (workflow_rule["condition_type"] == "domain" and workflow_rule["domain"])
            or (
                workflow_rule["condition_type"] == "criteria"
                and (
                    workflow_rule["criteria_partner_id"]
                    or workflow_rule["criteria_owner_id"]
                    or required_tag_ids_by_workflow_rule.get(workflow_rule["id"])
                    or excluded_tag_ids_by_workflow_rule.get(workflow_rule["id"])
                )
            )
        )

        server_actions.append(
            {
                "name": workflow_rule_name,
                "upg_name": f"{workflow_rule_id}_{workflow_rule_name}",
                "code": "\n".join(code),
                "children": children,
                # If there are criterion not supported by the new version, don't pin the action to the folder
                "folder_id": workflow_rule["domain_folder_id"] if not has_criterion else False,
            }
        )

    for operation, tag_id in chain(zip(cycle(["remove"]), all_tag_ids_remove), zip(cycle(["add"]), all_tag_ids_add)):
        if operation == "remove":
            name = f"Remove Tag {tag_info[tag_id]['name']}"
            upg_name = f"ir_actions_server_tag_remove_{sanitize(tag_info[tag_id]['name'])}_{tag_info[tag_id]}"
            sequence = 7
        else:  # add
            name = f"Add Tag {tag_info[tag_id]['name']}"
            upg_name = f"ir_actions_server_tag_add_{sanitize(tag_info[tag_id]['name'])}_{tag_info[tag_id]}"
            sequence = 10
        if upg_name in existing_server_act:
            continue
        queries_step_1.append(
            build_insert_ir_act_server(
                cr=cr,
                internal_id=internal_id,
                model_id=document_model_id,
                name=name,
                upg_name=upg_name,
                sequence=sequence,
                state="object_write",
                update_field_id=documents_tag_ids_field,
                update_related_model_id=documents_tag_model,
                selection_value=None,
                update_path="tag_ids",
                update_m2m_operation=operation,
                update_boolean_value="true",
                evaluation_type="value",
                resource_ref=f"documents.tag,{documents_tag_ids_field}",
                value=str(tag_id),
                crud_model_id=document_model_id,
            )
        )

    queries_step_2 = []
    queries_step_3 = []
    for server_action in server_actions:
        name = server_action["name"]
        upg_name = server_action["upg_name"]
        suffix_code = "_custom_code" if server_action["children"] else ""
        if server_action["code"]:
            queries_step_1.append(
                build_insert_ir_act_server(
                    cr=cr,
                    internal_id=internal_id,
                    model_id=document_model_id,
                    name=f"{name}{suffix_code}",
                    upg_name=f"{upg_name}{suffix_code}",
                    sequence=20,
                    state="code",
                    code=server_action["code"],
                )
            )
        if server_action["children"]:
            queries_step_2.append(
                build_insert_ir_act_server(
                    cr=cr,
                    internal_id=internal_id,
                    model_id=document_model_id,
                    name=name,
                    upg_name=upg_name,
                    sequence=20,
                    state="multi",
                    child_names=server_action["children"]
                    + ([f"{upg_name}{suffix_code}"] if server_action["code"] else []),
                )
            )

        if server_action["folder_id"]:
            # As in the new version, the only supported condition to display an action is the current folder, we only pin the action
            # on the folder if there were no additional condition (the action will be created but not linked to a folder).
            queries_step_3.append(
                cr.mogrify(
                    """
                    WITH inserted_ea AS (
                        INSERT INTO ir_embedded_actions("create_uid", "create_date", "write_uid", "write_date", "name", "parent_action_id", "action_id", "parent_res_model", "parent_res_id", "sequence")
                             SELECT 1, -- create_uid
                                    now() at time zone 'utc', -- create_date
                                    1, -- write_uid
                                    now() at time zone 'utc', -- write_date
                                    jsonb_build_object('en_US', %s), -- name
                                    %s, -- parent_action_id
                                    ir_act_server.id, -- action_id
                                    'documents.document', -- parent_res_model
                                    %s, -- parent_res_id
                                    nextval('_upg_document_sequence_action') -- sequence
                               FROM ir_act_server
                              WHERE _upg_name = %s
                        RETURNING id
                    )
                    INSERT INTO ir_embedded_actions_res_groups_rel("ir_embedded_actions_id", "res_groups_id")
                         SELECT id, %s
                           FROM inserted_ea
                    """,
                    [
                        server_action["name"],
                        documents_action_id,
                        server_action["folder_id"],
                        server_action["upg_name"],
                        internal_id,
                    ],
                )
            )
    return queries_step_1, queries_step_2, queries_step_3
