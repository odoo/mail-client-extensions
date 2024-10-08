from odoo.upgrade.util.spreadsheet import iter_commands


def migrate(cr, version):
    for commands in iter_commands(cr, like_all=[r"%\_PIVOT%"]):
        for command in commands:
            if command["type"] not in ("ADD_PIVOT", "UPDATE_PIVOT"):
                continue
            pivot = command["pivot"]
            pivot["columns"] = [migrate_dimension(col) for col in pivot["columns"]]
            pivot["rows"] = [migrate_dimension(row) for row in pivot["rows"]]
            pivot["measures"] = [migrate_measure(measure) for measure in pivot["measures"]]


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
