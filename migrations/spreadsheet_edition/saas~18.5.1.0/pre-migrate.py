from odoo.upgrade.util.spreadsheet import iter_commands


def migrate(cr, version):
    for commands in iter_commands(cr, like_any=[r"%ADD\_GLOBAL\_FILTER%", r"%EDIT\_GLOBAL\_FILTER%"]):
        for command in commands:
            if command["type"] in ("ADD_GLOBAL_FILTER", "EDIT_GLOBAL_FILTER") and command["filter"].get("defaultValue"):
                global_filter = command["filter"]
                if global_filter["type"] == "relation":
                    operator = "child_of" if global_filter.get("includeChildren") else "in"
                    global_filter["defaultValue"] = {
                        "operator": operator,
                        "ids": global_filter["defaultValue"],
                    }
                elif global_filter["type"] == "text":
                    global_filter["defaultValue"] = {
                        "operator": "ilike",
                        "strings": global_filter["defaultValue"],
                    }
                elif global_filter["type"] == "boolean":
                    if len(global_filter["defaultValue"]) != 1:
                        # [True, False] is no longer supported
                        # it's equivalent to no filter (except for 'active' field)
                        del global_filter["defaultValue"]
                    else:
                        operator = "set" if global_filter["defaultValue"][0] else "not set"
                        global_filter["defaultValue"] = {"operator": operator}
