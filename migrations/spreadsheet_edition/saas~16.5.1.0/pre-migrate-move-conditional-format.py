# -*- coding: utf-8 -*-

import json


def migrate(cr, version):
    cr.execute(
        r"""
        SELECT id, commands
          FROM spreadsheet_revision
         WHERE commands LIKE '%MOVE\_CONDITIONAL\_FORMAT%'
        """
    )

    for revision_id, data in cr.fetchall():
        data_loaded = json.loads(data)
        commands = data_loaded.get("commands", [])
        if not commands:
            continue

        changed = False
        for command in commands:
            if command["type"] != "MOVE_CONDITIONAL_FORMAT":
                continue

            command["type"] = "CHANGE_CONDITIONAL_FORMAT_PRIORITY"
            direction = command["direction"]
            command["delta"] = 1 if direction == "up" else -1
            del command["direction"]
            changed = True

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
