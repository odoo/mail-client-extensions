# -*- coding: utf-8 -*-

import json


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
        for command in commands:
            if command["type"] != "INSERT_PIVOT":
                continue
            changed = True
            definition = command["definition"]
            meta_data = definition.get("metaData", {})
            search_params = definition.get("searchParams", {})
            new_definition = {
                "colGroupBys": meta_data.get("colGroupBys", []),
                "rowGroupBys": meta_data.get("rowGroupBys", []),
                "measures": meta_data.get("activeMeasures", []),
                "model": meta_data.get("resModel"),
                "domain": search_params.get("domain", []),
                "context": search_params.get("context", {}),
                "name": definition.get("name"),
                "sortedColumn": meta_data.get("sortedColumn"),
            }
            command["definition"] = new_definition

        if not changed:
            continue

        data_loaded["commands"] = commands
        cr.execute(
            """
            UPDATE spreadsheet_revision
               SET commands=%s
             WHERE id=%s
            """,
            [json.dumps(data_loaded), revision_id],
        )
