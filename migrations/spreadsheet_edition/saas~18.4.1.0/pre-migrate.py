from odoo.upgrade.util.spreadsheet import iter_commands

DEFAULT_VALUE_MAP = {
    "last_week": "last_7_days",
    "last_month": "last_30_days",
    "last_three_months": "last_90_days",
    "last_year": "last_12_months",
}


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
            if global_filter["type"] == "date" and "defaultValue" in global_filter:
                if global_filter["defaultValue"] in ("last_six_month", "last_three_years"):
                    del global_filter["defaultValue"]
                elif global_filter["defaultValue"] in DEFAULT_VALUE_MAP:
                    global_filter["defaultValue"] = DEFAULT_VALUE_MAP[global_filter["defaultValue"]]
            if "rangeType" in global_filter:
                del global_filter["rangeType"]
            if "disabledPeriods" in global_filter:
                del global_filter["disabledPeriods"]
