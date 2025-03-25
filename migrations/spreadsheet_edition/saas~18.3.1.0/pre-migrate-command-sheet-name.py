from odoo.upgrade.util.spreadsheet import iter_commands


def migrate(cr, version):
    sheet_editing_cmds = ["DELETE_SHEET", "MOVE_COLUMNS_ROWS", "REMOVE_COLUMNS_ROWS", "ADD_COLUMNS_ROWS"]
    for commands in iter_commands(
        cr, like_any=["%{}%".format(cmd.replace("_", r"\_")) for cmd in [*sheet_editing_cmds, "RENAME_SHEET"]]
    ):
        for command in commands:
            if command["type"] in sheet_editing_cmds:
                command["sheetName"] = ""
            elif command["type"] == "RENAME_SHEET":
                command["newName"] = command.pop("name", "")
                command["oldName"] = ""
