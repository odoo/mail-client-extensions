from odoo.upgrade.util.spreadsheet import iter_commands


def migrate(cr, version):
    for commands in iter_commands(cr, like_all=[r"%CREATE\_FILTER\_TABLE%"]):
        for command in commands:
            if command["type"] == "CREATE_FILTER_TABLE":
                command["type"] = "CREATE_TABLE"
                sheet_id = command["sheetId"]
                command["ranges"] = [{"_sheetId": sheet_id, "_zone": zone} for zone in command["target"]]
                del command["target"]
