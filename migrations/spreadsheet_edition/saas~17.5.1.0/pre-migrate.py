import json


def migrate(cr, version):
    cr.execute(
        r"""
        SELECT id, commands
          FROM spreadsheet_revision
         WHERE commands LIKE '%\_PIVOT%'
        """
    )

    for revision_id, data in cr.fetchall():
        data_loaded = json.loads(data)
        commands = data_loaded.get("commands", [])
        if not commands:
            continue

        for command in commands:
            if command["type"] not in ("ADD_PIVOT", "UPDATE_PIVOT"):
                continue
            pivot = command["pivot"]
            pivot["columns"] = [migrate_dimension(col) for col in pivot["columns"]]
            pivot["rows"] = [migrate_dimension(row) for row in pivot["rows"]]
            pivot["measures"] = [migrate_measure(measure) for measure in pivot["measures"]]

        data_loaded["commands"] = commands
        cr.execute(
            """
            UPDATE spreadsheet_revision
               SET commands=%s
             WHERE id=%s
            """,
            [json.dumps(data_loaded), revision_id],
        )


def migrate_dimension(dimension):
    result = {
        "fieldName": dimension.get("name"),
        "id": dimension.get("name"),
    }
    if "granularity" in dimension:
        result["granularity"] = dimension["granularity"]
    if "order" in dimension:
        result["order"] = dimension["order"]
    return result


def migrate_measure(measure):
    result = {
        "fieldName": measure.get("name"),
        "id": measure.get("name"),
    }
    if "aggregator" in measure:
        result["aggregator"] = measure["aggregator"]
    return result
