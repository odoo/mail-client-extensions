# -*- coding: utf-8 -*-
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
               isol.evaluation_type,
               isol.value
          FROM ir_server_object_lines AS isol
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
    util.create_column(cr, "ir_act_server", "link_field_id", "integer")
    util.create_column(cr, "ir_act_server", "update_field_id", "integer")
    execute_values(
        cr._obj,
        r"""
            UPDATE ir_act_server
               SET state = data.state,
                   code = data.code,
                   evaluation_type = data.evaluation_type,
                   value = data.value,
                   crud_model_id = data.crud_model_id::INTEGER,
                   link_field_id = data.link_field_id::INTEGER,
                   update_field_id = data.update_field_id::INTEGER
              FROM (VALUES %s) AS data(
                       id,
                       state,
                       code,
                       evaluation_type,
                       value,
                       crud_model_id,
                       link_field_id,
                       update_field_id
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
            )
            for action in to_update
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
        # get code snippet
        code_snippet = compile_code_snippet(action, actions)
        # update the action to be a code action
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
            }
        )

    if len(res) > 0:
        util.add_to_migration_reports(
            """
            <details>
                <summary>
                    Following server actions which create or update records
                    had to be converted to code actions.
                    <br/>
                    You should verify that their code is correct.
                </summary>
                <ul>%s</ul>
            </details>
            """
            % (
                "\n".join(
                    "<li>{}</li>".format(
                        util.get_anchor_link_to_record(
                            "ir.actions.server", action["action_server_id"], action["name"]["en_US"]
                        )
                    )
                    for action in res
                )
            ),
            "Server Actions",
            format="html",
        )

    return res


def compile_code_snippet(action, all_actions):
    def get_update_field_value(a):
        if a["evaluation_type"] == "equation":
            return a["value"]
        elif a["evaluation_type"] == "reference":
            return f"env['{a['update_field_relation']}'].browse({int(a['value'])})"
        elif a["update_field_type"] in ("many2one", "integer"):
            with suppress(ValueError):
                return int(a["value"])
        return f"'{a['value']}'"

    # get same actions
    same_actions = [a for a in all_actions if a["action_server_id"] == action["action_server_id"]]
    # prepare the record data, using same actions (they are duplicates with different fields_lines)
    record_data = {action["update_field_name"]: get_update_field_value(action) for action in same_actions}
    # prepare the values string snippet
    values_snippet = "{" + ", ".join(f'"{k}": {v}' for k, v in record_data.items()) + "}"

    if action["state"] == "object_write":
        return f"record.write({values_snippet})"

    elif action["state"] == "object_create":
        # prepare the link snippet
        link_snippet = ""
        if action["link_field_id"]:
            link_snippet = "# link the new record to the current record\n"
            if action["link_field_type"] in ("one2many", "many2many"):
                link_snippet += (
                    f"""record.write({'{"' + action['link_field_name'] + '": [Command.link(new_record.id)]}'})"""
                )
            else:
                link_snippet += f"""record.write({'{"' + action['link_field_name'] + '": new_record.id}'})"""

        return f"""
new_record = env["{action['crud_model_name']}"].create({values_snippet})
{link_snippet}
"""
    return None
