import re
from uuid import uuid4

from odoo.upgrade import util
from odoo.upgrade.util import json
from odoo.upgrade.util.spreadsheet import iter_commands


def migrate(cr, version):
    if not util.table_exists(cr, "spreadsheet_revision"):
        return
    for commands in iter_commands(cr, like_any=[r"%ADD\_PIVOT%", r"%UPDATE\_CELL%"]):
        pivot_update_cell = [cmd for cmd in commands if (cmd.get("type") == "UPDATE_CELL" and cmd.get("content"))]
        for cmd in pivot_update_cell:
            cmd["content"] = re.sub(r"=PIVOT(\(|\.HEADER)", r"=ODOO.PIVOT\1", cmd["content"], flags=re.I)
        is_pivot_insertion = commands[0]["type"] == "ADD_PIVOT"
        pivot = commands[0].get("pivot")
        if not pivot and is_pivot_insertion:
            continue

        formulas = [
            cmd for cmd in commands if (cmd.get("type") == "ADD_PIVOT_FORMULA" and cmd.get("formula") == "PIVOT.HEADER")
        ]
        if not formulas:
            continue
        # The first formula is the top left column
        anchor = {"col": formulas[0].get("col", 1) - 1, "row": formulas[0].get("row", 0)}

        rows = [cmd for cmd in formulas if cmd.get("col") == anchor["col"]]
        pivot_id = rows[0].get("args", [0])[0]
        table_rows = []
        for cell in rows:
            args = cell.get("args")[1:]  # Remove id
            table_rows.append({"fields": args[::2], "values": args[1::2], "indent": len(args[::2])})

        cols = [cmd for cmd in formulas if cmd.get("col") != 0]
        number_cols = rows[0].get("row", 0)
        table_cols = []
        for i in range(anchor["row"], number_cols):
            cells = [cmd for cmd in cols if cmd.get("row") == i]
            row_without_width = []
            for cell in cells:
                args = cell.get("args")[1:]  # Remove id
                row_without_width.append(
                    {
                        "fields": args[::2],
                        "values": args[1::2],
                    }
                )
            # Compute width
            row_with_width = []
            current_cell = row_without_width.pop(0)
            width = 1
            while len(row_without_width):
                next_cell = row_without_width.pop(0)
                if json.dumps(current_cell) == json.dumps(next_cell):
                    width += 1
                else:
                    current_cell["width"] = width
                    row_with_width.append(current_cell)
                    current_cell = next_cell
                    width = 1

            current_cell["width"] = width
            row_with_width.append(current_cell)

            table_cols.append(row_with_width)

        table_measures = list({cell["values"][-1] for cell in table_cols[-1]})
        payload = {
            "type": "INSERT_PIVOT" if is_pivot_insertion else "RE_INSERT_PIVOT",
            "sheetId": formulas[0].get("sheetId"),
            "col": anchor["col"],
            "row": anchor["row"],
            "table": {
                "cols": table_cols,
                "rows": table_rows,
                "measures": table_measures,
            },
            "id": pivot_id,
        }
        if is_pivot_insertion:
            payload.update(
                {
                    "dataSourceId": str(uuid4()),
                    "definition": {
                        "metaData": {
                            "colGroupBys": pivot.get("colGroupBys"),
                            "rowGroupBys": pivot.get("rowGroupBys"),
                            "activeMeasures": table_measures,
                            "resModel": pivot.get("model"),
                        },
                        "searchParams": {
                            "comparision": None,
                            "context": pivot.get("context"),
                            "domain": pivot.get("domain"),
                            "groupBy": [],
                            "orderBy": [],
                        },
                        "name": pivot.get("model"),
                    },
                }
            )
        commands.clear()
        commands.append(payload)
