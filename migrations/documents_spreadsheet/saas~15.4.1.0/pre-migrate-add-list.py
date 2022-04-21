# -*- coding: utf-8 -*-

import json
from uuid import uuid4

from odoo.upgrade import util


def migrate(cr, version):
    if not util.table_exists(cr, "spreadsheet_revision"):
        return
    cr.execute(
        """
        SELECT id, commands
          FROM spreadsheet_revision
         WHERE commands LIKE '%ADD_ODOO_LIST%'
        """
    )

    for revision_id, data in cr.fetchall():
        data = json.loads(data)
        commands = data.get("commands", [])
        if not commands:
            continue
        is_list_insertion = commands[0]["type"] == "ADD_ODOO_LIST"
        list = commands[0].get("list")
        if not list and is_list_insertion:
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

        columns = []
        for cell in headers:
            columns.append(
                {
                    "name": cell["args"][1],
                    # Type is only needed to format the column, but we cannot
                    # infer them from these commands.
                    "type": "",
                }
            )

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
                            "resModel": list.get("model"),
                            "columns": [col["name"] for col in columns],
                        },
                        "searchParams": {
                            "context": list.get("context"),
                            "domain": list.get("domain"),
                            "orderBy": [],
                        },
                        "name": list.get("model"),
                    },
                }
            )
        data["commands"] = [payload]
        cr.execute(
            """
            UPDATE spreadsheet_revision
                SET commands=%s
                WHERE id=%s
            """,
            [json.dumps(data), revision_id],
        )
