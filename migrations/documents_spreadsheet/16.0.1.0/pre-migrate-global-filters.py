# -*- coding: utf-8 -*-

import json


def migrate(cr, version):
    cr.execute(
        r"""
        SELECT id, commands
          FROM spreadsheet_revision
         WHERE commands LIKE '%\_GLOBAL\_FILTER%'
        """
    )

    for revision_id, data in cr.fetchall():
        data = json.loads(data)
        commands = data.get("commands", [])
        if not commands:
            continue

        changed = False
        for command in commands:
            if "_GLOBAL_FILTER" not in command["type"] or "filter" not in command:
                continue

            if command["filter"]["type"] == "date" and "year" in command["filter"]["defaultValue"]:
                default = command["filter"]["defaultValue"]
                if default["year"] == "this_year":
                    default["yearOffset"] = 0
                elif default["year"] == "last_year":
                    default["yearOffset"] = -1
                elif default["year"] == "antepenultimate_year":
                    default["yearOffset"] = -2
                del default["year"]
                changed = True

        if not changed:
            continue

        data["commands"] = commands
        cr.execute(
            """
            UPDATE spreadsheet_revision
                SET commands=%s
                WHERE id=%s
            """,
            [json.dumps(data), revision_id],
        )
