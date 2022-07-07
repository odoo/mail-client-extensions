# -*- coding: utf-8 -*-

import json


def migrate(cr, version):
    cr.execute(
        r"""
        SELECT id, commands
          FROM spreadsheet_revision
         WHERE commands LIKE '%ADD\_CONDITIONAL\_FORMAT%'
        """
    )

    for revision_id, data in cr.fetchall():
        data = json.loads(data)
        commands = data.get("commands", [])
        if not commands:
            continue

        for command in commands:
            sheet_id = command["sheetId"]
            command["ranges"] = [{"_sheetId": sheet_id, "_zone": zone} for zone in command["target"]]
            del command["target"]

        data["commands"] = commands
        cr.execute(
            """
            UPDATE spreadsheet_revision
                SET commands=%s
                WHERE id=%s
            """,
            [json.dumps(data), revision_id],
        )
