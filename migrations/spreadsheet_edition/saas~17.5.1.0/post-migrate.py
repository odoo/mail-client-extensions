import json


def migrate(cr, version):
    cr.execute("SELECT code, week_start FROM res_lang")
    week_starts = dict(cr.fetchall())
    cr.execute(
        r"""
        SELECT id, commands
          FROM spreadsheet_revision
         WHERE commands LIKE '%UPDATE\_LOCALE%'
        """
    )
    for revision_id, data in cr.fetchall():
        data_loaded = json.loads(data)
        commands = data_loaded.get("commands", [])
        if not commands:
            continue

        for command in commands:
            if command["type"] != "UPDATE_LOCALE":
                continue
            command["locale"]["weekStart"] = int(week_starts.get(command["locale"]["code"], 1))

        data_loaded["commands"] = commands
        cr.execute(
            """
            UPDATE spreadsheet_revision
               SET commands=%s
             WHERE id=%s
            """,
            [json.dumps(data_loaded), revision_id],
        )
