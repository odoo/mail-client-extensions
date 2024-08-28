import json


def migrate(cr, version):
    cr.execute(
        r"""
        SELECT id, commands
          FROM spreadsheet_revision
         WHERE commands LIKE '%CREATE\_FILTER\_TABLE%'
        """
    )

    for revision_id, data in cr.fetchall():
        data_loaded = json.loads(data)
        if "commands" not in data_loaded:
            continue

        changed = False
        for command in data_loaded["commands"]:
            if command["type"] == "CREATE_FILTER_TABLE":
                command["type"] = "CREATE_TABLE"
                sheet_id = command["sheetId"]
                command["ranges"] = [{"_sheetId": sheet_id, "_zone": zone} for zone in command["target"]]
                del command["target"]
                changed = True

        if changed:
            cr.execute(
                """
                UPDATE spreadsheet_revision
                    SET commands=%s
                WHERE id=%s
                """,
                [json.dumps(data_loaded), revision_id],
            )
