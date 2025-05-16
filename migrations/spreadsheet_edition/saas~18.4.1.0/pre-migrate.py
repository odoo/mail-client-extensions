from odoo.upgrade.util.spreadsheet import iter_commands


def migrate(cr, version):
    for commands in iter_commands(cr, like_any=[r"%ADD\_GLOBAL\_FILTER%", r"%EDIT\_GLOBAL\_FILTER%"]):
        for command in commands:
            if command["type"] not in ("ADD_GLOBAL_FILTER", "EDIT_GLOBAL_FILTER"):
                continue
            global_filter = command["filter"]
            if global_filter["type"] == "text" and "defaultValue" in global_filter:
                global_filter["defaultValue"] = [global_filter["defaultValue"]]
