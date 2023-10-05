# -*- coding: utf-8 -*-

import json


def migrate(cr, version):
    cr.execute(
        r"""
        SELECT id, commands
          FROM spreadsheet_revision
         WHERE commands LIKE '%ADD\_GLOBAL\_FILTER%'
            OR commands LIKE '%EDIT\_GLOBAL\_FILTER%'
        """
    )

    for revision_id, data in cr.fetchall():
        data_loaded = json.loads(data)
        commands = data_loaded.get("commands", [])
        if not commands:
            continue

        changed = False
        for command in commands:
            if command["type"] not in ("ADD_GLOBAL_FILTER", "EDIT_GLOBAL_FILTER"):
                continue
            global_filter = command["filter"]
            if global_filter["type"] == "date" and global_filter["rangeType"] in ("year", "quarter", "month"):
                if "defaultsToCurrentPeriod" in global_filter:
                    if global_filter["defaultsToCurrentPeriod"]:
                        global_filter["defaultValue"] = f"this_{command['filter']['rangeType']}"
                    del global_filter["defaultsToCurrentPeriod"]
                global_filter["rangeType"] = "fixedPeriod"
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
