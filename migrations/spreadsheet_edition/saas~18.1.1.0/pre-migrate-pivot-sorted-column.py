from odoo.upgrade.util.spreadsheet import iter_commands


def migrate(cr, version):
    for commands in iter_commands(cr, like_all=[r"%\_PIVOT%"]):
        for command in commands:
            if command["type"] not in ("ADD_PIVOT", "UPDATE_PIVOT"):
                continue
            pivot = command["pivot"]
            sortedColumn = pivot.get("sortedColumn")
            if not sortedColumn:
                continue
            groupId = sortedColumn.get("groupId")
            measure = next((m for m in pivot["measures"] if m["fieldName"] == sortedColumn["measure"]), None)
            if measure and groupId and len(groupId) == 2 and len(groupId[1]) == 0:
                pivot["sortedColumn"] = {
                    "measure": measure["id"],
                    "order": sortedColumn.get("order"),
                    "domain": [],
                }
            else:
                del pivot["sortedColumn"]
