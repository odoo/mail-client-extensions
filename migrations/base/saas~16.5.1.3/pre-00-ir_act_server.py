from contextlib import suppress

from psycopg2.extras import execute_values

from odoo.upgrade import util


def migrate(cr, version):
    # fetch server actions to migrate
    query = r"""
        SELECT act.id AS action_server_id,
               act.name,
               act.state,
               act.crud_model_id,
               im.model AS crud_model_name,
               act.link_field_id,
               imf1.name  AS link_field_name,
               imf1.ttype AS link_field_type,
               isol.col1     AS update_field_id,
               imf2.relation AS update_field_relation,
               imf2.name     AS update_field_name,
               imf2.ttype    AS update_field_type,
               fs.id         AS selection_value,
               isol.evaluation_type,
               isol.value
          FROM ir_server_object_lines AS isol
               LEFT JOIN ir_model_fields_selection AS fs
               ON fs.value = isol.value
               AND fs.field_id = isol.col1

               LEFT JOIN ir_act_server AS act
               ON act.id = isol.server_id

               LEFT JOIN ir_model AS im
               ON im.id = act.crud_model_id

               LEFT JOIN ir_model_fields AS imf1
               ON imf1.id = act.link_field_id

               LEFT JOIN ir_model_fields AS imf2
               ON imf2.id = isol.col1
         WHERE act.state IN ('object_create', 'object_write')
         ORDER BY act.sequence, act.id, isol.col1
    """
    cr.execute(query)
    results = cr.dictfetchall()
    to_update = process_actions(results)

    util.create_column(cr, "ir_act_server", "evaluation_type", "varchar")
    util.create_column(cr, "ir_act_server", "value", "varchar")
    util.create_column(cr, "ir_act_server", "update_path", "varchar")
    util.create_column(cr, "ir_act_server", "update_related_model_id", "int4")
    util.create_column(cr, "ir_act_server", "link_field_id", "integer")
    util.create_column(cr, "ir_act_server", "update_field_id", "integer")
    util.create_column(cr, "ir_act_server", "selection_value", "integer")
    execute_values(
        cr._obj,
        r"""
            UPDATE ir_act_server
               SET state = data.state,
                   code = data.code,
                   evaluation_type = data.evaluation_type,
                   value = data.value,
                   update_path = data.update_path,
                   crud_model_id = data.crud_model_id::INTEGER,
                   link_field_id = data.link_field_id::INTEGER,
                   update_field_id = data.update_field_id::INTEGER,
                   selection_value = data.selection_value::INTEGER
              FROM (VALUES %s) AS data(
                       id,
                       state,
                       code,
                       evaluation_type,
                       value,
                       crud_model_id,
                       link_field_id,
                       update_field_id,
                       selection_value,
                       update_path
                   )
             WHERE ir_act_server.id = data.id
        """,
        [
            (
                action["action_server_id"],
                action["state"],
                action["code"],
                action["evaluation_type"],
                action["value"],
                action["crud_model_id"],
                action["link_field_id"],
                action["update_field_id"],
                action["selection_value"],
                action["update_path"],
            )
            for action in to_update
        ],
    )

    # migrated to code server actions should be
    # excluded from the cloc for maintenance fees
    execute_values(
        cr._obj,
        r"""
            INSERT INTO ir_model_data (name, module, model, res_id, noupdate)
                 VALUES %s
        """,
        [
            (
                action["__cloc_exclude_name"],
                "__cloc_exclude__",
                "ir.actions.server",
                action["action_server_id"],
                True,
            )
            for action in to_update
            if action["__include_in_migration_report"]
        ],
    )

    util.remove_field(cr, "ir.actions.server", "fields_lines")
    util.remove_model(cr, "ir.server.object.lines")


def process_actions(actions):
    res = []
    processed_ids = []
    for action in actions:
        if action["action_server_id"] in processed_ids:
            continue
        processed_ids.append(action["action_server_id"])
        # get same actions
        same_actions = [a for a in actions if a["action_server_id"] == action["action_server_id"]]
        if len(same_actions) == 1 and (
            (
                action["state"] == "object_create"
                and action["evaluation_type"] == "value"
                and action["update_field_name"] == "name"
            )
            or (action["state"] == "object_write")
        ):
            # There is only one field line and it can still be handled by
            # object_create (only for "value" evaluation_type and "name" field)
            # or object_write action states.
            # This will avoid unnecessary code actions, which may lead
            # to unexpected maintenance fees.
            res.append(
                {
                    "action_server_id": action["action_server_id"],
                    "name": action["name"],
                    "state": action["state"],
                    "code": None,
                    "evaluation_type": action["evaluation_type"],
                    "value": action["value"],
                    "crud_model_id": action["crud_model_id"],
                    "link_field_id": action["link_field_id"],
                    "update_field_id": (None if action["state"] == "object_create" else action["update_field_id"]),
                    "selection_value": (action["selection_value"] if action["evaluation_type"] == "value" else None),
                    "update_path": (action["update_field_name"] if action["state"] == "object_write" else None),
                    "__include_in_migration_report": False,
                }
            )
            continue
        # get code snippet
        code_snippet = compile_code_snippet(same_actions)
        # update the action to be a code action
        # and exclude it from the cloc for maintenance fees
        res.append(
            {
                "action_server_id": action["action_server_id"],
                "name": action["name"],
                "state": "code",
                "code": code_snippet,
                "evaluation_type": None,
                "value": None,
                "crud_model_id": None,
                "link_field_id": None,
                "update_field_id": None,
                "selection_value": None,
                "update_path": None,
                "__include_in_migration_report": True,
                "__cloc_exclude_name": f"migrated_to_code_server_action_{action['action_server_id']}",
            }
        )

    to_report = [act for act in res if act["__include_in_migration_report"]]
    if len(to_report) > 0:
        util.add_to_migration_reports(
            """
            <details>
                <summary>
                    Following server actions which create or update records
                    had to be converted to code actions.
                    <br/>
                    You should verify that their code is correct.
                </summary>
                <ul>{}</ul>
            </details>
            """.format(
                "\n".join(
                    "<li>{}</li>".format(
                        util.get_anchor_link_to_record(
                            "ir.actions.server", action["action_server_id"], action["name"]["en_US"]
                        )
                    )
                    for action in to_report
                )
            ),
            "Server Actions",
            format="html",
        )

    return res


def compile_code_snippet(same_actions):
    def get_update_field_value(a):
        if a["evaluation_type"] == "equation":
            return a["value"]
        elif a["update_field_type"] in ("many2one", "integer") or a["evaluation_type"] == "reference":
            with suppress(ValueError):
                return int(a["value"])
        return f"'{a['value']}'"

    # prepare the record data, using same actions (they are duplicates with different fields_lines)
    record_data = {action["update_field_name"]: get_update_field_value(action) for action in same_actions}
    # prepare the values string snippet
    values_snippet = "{" + ", ".join(f'"{k}": {v}' for k, v in record_data.items()) + "}"

    # get first action
    first_action = same_actions[0]
    if first_action["state"] == "object_write":
        return f"record.write({values_snippet})"

    elif first_action["state"] == "object_create":
        # prepare the link snippet
        link_snippet = ""
        if first_action["link_field_id"]:
            link_snippet = "# link the new record to the current record\n"
            if first_action["link_field_type"] in ("one2many", "many2many"):
                link_snippet += (
                    f"""record.write({'{"' + first_action['link_field_name'] + '": [Command.link(new_record.id)]}'})"""
                )
            else:
                link_snippet += f"""record.write({'{"' + first_action['link_field_name'] + '": new_record.id}'})"""

        return f"""
new_record = env["{first_action['crud_model_name']}"].create({values_snippet})
{link_snippet}
"""
    return None
