# -*- coding: utf-8 -*-

import json
import re

from odoo.upgrade import util


def migrate(cr, version):
    if not util.table_exists(cr, "spreadsheet_revision"):
        return
    filter_command_pattern = re.compile("(EDIT|ADD|REMOVE)_PIVOT_FILTER")
    cr.execute("SELECT id, commands AS data FROM spreadsheet_revision")

    for revision in cr.dictfetchall():
        data = json.loads(revision["data"])
        commands = data["commands"]
        for command in commands:
            command["type"] = filter_command_pattern.sub("\\1_GLOBAL_FILTER", command["type"])
            if command["type"] in {"ADD_GLOBAL_FILTER", "EDIT_GLOBAL_FILTER"}:
                fields = command["filter"].pop("fields")
                command["filter"]["pivotFields"] = fields
        data["commands"] = commands
        cr.execute(
            """
            UPDATE spreadsheet_revision
               SET commands=%s
             WHERE id=%s
            """,
            [json.dumps(data), revision["id"]],
        )
