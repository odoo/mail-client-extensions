# -*- coding: utf-8 -*-

import json


def migrate(cr, version):
    cr.execute(
        r"""
        SELECT id, commands
          FROM spreadsheet_revision
         WHERE commands LIKE '%MOVE\_SHEET%'
        """
    )

    for revision_id, data in cr.fetchall():
        data = json.loads(data)
        commands = data.get("commands", [])
        if not commands:
            continue

        changed = False
        for command in commands:
            if command["type"] != "MOVE_SHEET":
                continue

            direction = command["direction"]
            command["delta"] = -1 if direction == "left" else 1
            del command["direction"]
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
