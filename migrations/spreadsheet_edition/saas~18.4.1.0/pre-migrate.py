from odoo.upgrade.util.spreadsheet import iter_commands


def migrate(cr, version):
    for commands in iter_commands(cr, like_any=[r"%ADD\_GLOBAL\_FILTER%", r"%EDIT\_GLOBAL\_FILTER%"]):
        for command in commands:
            if command["type"] not in ("ADD_GLOBAL_FILTER", "EDIT_GLOBAL_FILTER"):
                continue
            global_filter = command["filter"]
            # If the defaultValue is an empty value, we remove it
            if "defaultValue" in global_filter and not global_filter["defaultValue"]:
                del global_filter["defaultValue"]
            if global_filter["type"] == "text" and "defaultValue" in global_filter:
                global_filter["defaultValue"] = [global_filter["defaultValue"]]
            if global_filter["type"] == "text" and "rangeOfAllowedValues" in global_filter:
                global_filter["rangesOfAllowedValues"] = [global_filter["rangeOfAllowedValues"]]
                del global_filter["rangeOfAllowedValues"]
            if (
                global_filter["type"] == "date"
                and global_filter["rangeType"] == "fixedPeriod"
                and not isinstance(global_filter["defaultValue"], str)
            ):
                # If the defaultValue is not a string, it's probably a
                # something very old that we do not support anymore
                # See migration2to3(antepenultimate_year for example)
                # from migration.js in odoo.
                del global_filter["defaultValue"]
