from odoo.upgrade.util.spreadsheet import process_commands


def migrate(cr, version):
    def adapter(commands):
        changed = False
        for command in commands:
            if command["type"] != "MOVE_SHEET":
                continue

            direction = command["direction"]
            command["delta"] = -1 if direction == "left" else 1
            del command["direction"]
            changed = True
        return changed

    process_commands(cr, adapter, like_all=[r"%MOVE\_SHEET%"])
