import json


def migrate(cr, version):
    cr.execute(
        r"""
        SELECT id, commands
          FROM spreadsheet_revision
         WHERE commands LIKE '%\_CHART%'
        """
    )

    for revision_id, data in cr.fetchall():
        data_loaded = json.loads(data)
        commands = data_loaded.get("commands", [])
        if not commands:
            continue

        for command in commands:
            if command["type"] not in ["CREATE_CHART", "UPDATE_CHART"]:
                continue
            definition = command["definition"]
            # 1. title is now an object
            if "title" in definition:
                definition["title"] = {"text": definition["title"]}
            # 2. dataSets is now an object for chart combo, bar, line, scatter, waterfall
            if definition["type"] in ["combo", "bar", "line", "scatter", "waterfall"]:
                definition["dataSets"] = [{"dataRange": r} for r in definition.get("dataSets", [])]
            # 3. verticalAxisPosition is removed, except for waterfall chart
            if definition["type"] != "waterfall" and not definition["type"].startswith("odoo_"):
                definition.pop("verticalAxisPosition", None)

        data_loaded["commands"] = commands
        cr.execute(
            """
            UPDATE spreadsheet_revision
               SET commands=%s
             WHERE id=%s
            """,
            [json.dumps(data_loaded), revision_id],
        )
