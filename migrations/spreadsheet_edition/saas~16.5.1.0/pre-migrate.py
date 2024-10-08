from odoo.upgrade.util.spreadsheet import iter_commands


def migrate(cr, version):
    for commands in iter_commands(cr, like_any=[r"%ADD\_GLOBAL\_FILTER%", r"%EDIT\_GLOBAL\_FILTER%"]):
        for command in commands:
            if command["type"] not in ("ADD_GLOBAL_FILTER", "EDIT_GLOBAL_FILTER"):
                continue
            global_filter = command["filter"]
            if global_filter["type"] == "date" and global_filter["rangeType"] in ("year", "quarter", "month"):
                if "defaultsToCurrentPeriod" in global_filter:
                    if global_filter["defaultsToCurrentPeriod"]:
                        global_filter["defaultValue"] = f"this_{command['filter']['rangeType']}"
                    del global_filter["defaultsToCurrentPeriod"]
                global_filter["rangeType"] = "fixedPeriod"
