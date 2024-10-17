# ruff: noqa: PLW2901, SIM108
import json
import re
from ast import literal_eval

from odoo.upgrade import util


def migrate(cr, version):
    if not util.table_exists(cr, "spreadsheet_revision"):
        return
    filter_command_pattern = re.compile("(EDIT|ADD|REMOVE)_PIVOT_FILTER")
    cr.execute("SELECT id, commands FROM spreadsheet_revision")

    for revid, data in cr.fetchall():
        if "SNAPSHOT_CREATED" in data:
            # This command is not saved in db as JSON, but directly as a dict, which lead to invalid JSON: https://git.io/J1YDo
            data = literal_eval(data)
        else:
            data = json.loads(data)

        commands = data.get("commands", [])
        changed = False
        for command in commands:
            old_type = command["type"]
            command["type"] = filter_command_pattern.sub("\\1_GLOBAL_FILTER", old_type)
            if command["type"] != old_type:
                changed = True
            if command["type"] in {"ADD_GLOBAL_FILTER", "EDIT_GLOBAL_FILTER"}:
                fields = command["filter"].pop("fields")
                command["filter"]["pivotFields"] = fields
        if not changed:
            continue
        if commands:
            data["commands"] = commands

        cr.execute(
            """
            UPDATE spreadsheet_revision
               SET commands=%s
             WHERE id=%s
            """,
            [json.dumps(data), revid],
        )
