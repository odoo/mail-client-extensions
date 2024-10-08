import re
from uuid import uuid4

from odoo.upgrade import util
from odoo.upgrade.util.spreadsheet import iter_commands


def migrate(cr, version):
    if not util.table_exists(cr, "spreadsheet_revision"):
        return
    for commands in iter_commands(cr, like_any=[r"%ADD\_ODOO\_LIST%", r"%UPDATE\_CELL%"]):
        list_update_cell = [cmd for cmd in commands if (cmd.get("type") == "UPDATE_CELL" and cmd.get("content"))]
        for cmd in list_update_cell:
            cmd["content"] = re.sub(r"=LIST(\(|\.HEADER)", r"=ODOO.LIST\1", cmd["content"], flags=re.I)
        is_list_insertion = commands[0]["type"] == "ADD_ODOO_LIST"
        lst = commands[0].get("list")
        if not lst and is_list_insertion:
            continue

        headers = [
            cmd
            for cmd in commands
            if (
                cmd.get("type") == "ADD_ODOO_LIST_FORMULA"
                and cmd.get("formula") == "LIST.HEADER"
                and len(cmd.get("args", [])) > 1
            )
        ]
        if not headers:
            continue
        # The first formula is the top left column
        anchor = {"col": headers[0].get("col", 0), "row": headers[0].get("row", 0)}

        body = [
            cmd for cmd in commands if (cmd.get("type") == "ADD_ODOO_LIST_FORMULA" and cmd.get("formula") == "LIST")
        ]
        if not body:
            continue
        linesNumber = body[-1].get("row", 0) - anchor["row"]
        if not linesNumber:
            continue

        columns = [
            {
                "name": cell["args"][1],
                # Type is only needed to format the column, but we cannot
                # infer them from these commands.
                "type": "",
            }
            for cell in headers
        ]
        payload = {
            "type": "INSERT_ODOO_LIST" if is_list_insertion else "RE_INSERT_ODOO_LIST",
            "sheetId": headers[0].get("sheetId"),
            "col": anchor["col"],
            "row": anchor["row"],
            "id": headers[0]["args"][0],
            "linesNumber": linesNumber,
            "columns": columns,
        }
        if is_list_insertion:
            payload.update(
                {
                    "dataSourceId": str(uuid4()),
                    "definition": {
                        "metaData": {
                            "resModel": lst.get("model"),
                            "columns": [col["name"] for col in columns],
                        },
                        "searchParams": {
                            "context": lst.get("context"),
                            "domain": lst.get("domain"),
                            "orderBy": [],
                        },
                        "name": lst.get("model"),
                    },
                }
            )
        commands.clear()
        commands.append(payload)
