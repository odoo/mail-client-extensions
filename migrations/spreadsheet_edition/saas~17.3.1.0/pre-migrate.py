# -*- coding: utf-8 -*-

import json
import re


def migrate(cr, version):
    cr.execute(
        r"""
        SELECT id, commands
          FROM spreadsheet_revision
         WHERE commands LIKE '%UPDATE\_CELL%'
        """
    )

    for revision_id, data in cr.fetchall():
        data_loaded = json.loads(data)
        commands = data_loaded.get("commands", [])
        if not commands:
            continue

        for command in commands:
            if command["type"] != "UPDATE_CELL":
                continue
            command["content"] = re.sub(r"\bODOO\.PIVOT\(", "PIVOT.VALUE(", command["content"], flags=re.I)
            command["content"] = re.sub(r"\bODOO\.PIVOT\.TABLE\b", "PIVOT", command["content"], flags=re.I)
            command["content"] = re.sub(r"\bODOO\.PIVOT\.HEADER\b", "PIVOT.HEADER", command["content"], flags=re.I)

        data_loaded["commands"] = commands
        cr.execute(
            """
            UPDATE spreadsheet_revision
               SET commands=%s
             WHERE id=%s
            """,
            [json.dumps(data_loaded), revision_id],
        )
