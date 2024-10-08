from odoo.upgrade.util.spreadsheet import iter_commands


def migrate(cr, version):
    for commands in iter_commands(cr, like_all=[r"%MOVE\_CONDITIONAL\_FORMAT%"]):
        for command in commands:
            if command["type"] != "MOVE_CONDITIONAL_FORMAT":
                continue

            command["type"] = "CHANGE_CONDITIONAL_FORMAT_PRIORITY"
            direction = command["direction"]
            command["delta"] = 1 if direction == "up" else -1
            del command["direction"]
