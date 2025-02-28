from odoo.upgrade.util.spreadsheet import iter_commands


def migrate(cr, version):
    for commands in iter_commands(cr, like_any=[r"%ADD\_PIVOT%", r"%UPDATE\_PIVOT%"]):
        for command in commands:
            if command["type"] not in ("ADD_PIVOT", "UPDATE_PIVOT"):
                continue
            pivot = command["pivot"]
            sorted_column = pivot.get("sortedColumn")
            if not sorted_column:
                continue
            measures = [m["id"] for m in pivot["measures"]]
            if pivot["sortedColumn"]["measure"] not in measures:
                del pivot["sortedColumn"]
