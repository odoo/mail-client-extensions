# -*- coding: utf-8 -*-

import json

from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        r"""
        SELECT id, commands
          FROM spreadsheet_revision
         WHERE commands LIKE '%INSERT\_PIVOT%'
        """
    )

    for revision_id, data in cr.fetchall():
        data_loaded = json.loads(data)
        commands = data_loaded.get("commands", [])
        if not commands:
            continue

        changed = False
        new_commands = []
        for command in commands:
            if command["type"] != "INSERT_PIVOT":
                new_commands.append(command)
                continue
            changed = True
            definition = command["definition"]
            meta_data = definition.get("metaData", {})
            search_params = definition.get("searchParams", {})
            pivot = {
                "colGroupBys": meta_data.get("colGroupBys", []),
                "rowGroupBys": meta_data.get("rowGroupBys", []),
                "measures": meta_data.get("activeMeasures", []),
                "model": meta_data.get("resModel"),
                "domain": search_params.get("domain", []),
                "context": search_params.get("context", {}),
                "name": definition.get("name"),
                "sortedColumn": meta_data.get("sortedColumn"),
                "type": "ODOO",
            }
            del command["definition"]

            new_commands.append(
                {
                    "type": "ADD_PIVOT",
                    "id": command["id"],
                    "pivot": pivot,
                }
            )

            new_commands.append(command)

        if not changed:
            continue

        data_loaded["commands"] = new_commands
        cr.execute(
            """
            UPDATE spreadsheet_revision
               SET commands=%s
             WHERE id=%s
            """,
            [json.dumps(data_loaded), revision_id],
        )

    util.rename_field(cr, "spreadsheet.revision", "revision_id", "revision_uuid")
    util.rename_field(cr, "spreadsheet.mixin", "server_revision_id", "current_revision_uuid")
    util.remove_constraint(cr, "spreadsheet_revision", "spreadsheet_revision_parent_revision_unique")
    cr.execute("CREATE INDEX spreadsheet_revision__revision_uuid_index ON spreadsheet_revision(revision_uuid)")

    cr.execute(
        """
        ALTER TABLE spreadsheet_revision RENAME COLUMN parent_revision_id TO _parent_revision_id_upg;
        ALTER TABLE spreadsheet_revision ADD COLUMN parent_revision_id int4;
        """
    )
    util.explode_execute(
        cr,
        """
        UPDATE spreadsheet_revision r
           SET parent_revision_id = p.id
          FROM spreadsheet_revision p
         WHERE p.revision_uuid = r._parent_revision_id_upg
           AND p.res_id = r.res_id
           AND p.res_model = r.res_model
        """,
        table="spreadsheet_revision",
        alias="r",
    )
    cr.execute("ALTER TABLE spreadsheet_revision DROP COLUMN _parent_revision_id_upg")
