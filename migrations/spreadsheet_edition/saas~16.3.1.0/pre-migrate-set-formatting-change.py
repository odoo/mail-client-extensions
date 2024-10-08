from odoo.upgrade.util.spreadsheet import iter_commands


def migrate(cr, version):
    for commands in iter_commands(cr, like_all=[r"%SET\_FORMATTING%", "%border%"]):
        new_commands = []
        for formatting_command in commands:
            if formatting_command.get("type") == "SET_FORMATTING" and "border" in formatting_command:
                if "style" in formatting_command or "format" in formatting_command:
                    new_commands.append(
                        {
                            "type": "SET_ZONE_BORDERS",
                            "sheetId": formatting_command["sheetId"],
                            "target": formatting_command["target"],
                            "border": {
                                "position": formatting_command["border"],
                            },
                        }
                    )
                    del formatting_command["border"]
                else:
                    formatting_command["type"] = "SET_ZONE_BORDERS"
                    formatting_command["border"] = {"position": formatting_command["border"]}
            new_commands.append(formatting_command)
        commands.clear()
        commands.extend(new_commands)
