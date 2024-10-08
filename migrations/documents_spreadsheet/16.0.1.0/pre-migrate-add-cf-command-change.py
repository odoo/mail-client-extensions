from odoo.upgrade.util.spreadsheet import iter_commands


def migrate(cr, version):
    for commands in iter_commands(cr, like_all=[r"%ADD\_CONDITIONAL\_FORMAT%"]):
        for command in commands:
            if command["type"] != "ADD_CONDITIONAL_FORMAT":
                continue

            sheet_id = command["sheetId"]
            command["ranges"] = [{"_sheetId": sheet_id, "_zone": zone} for zone in command["target"]]
            del command["target"]
