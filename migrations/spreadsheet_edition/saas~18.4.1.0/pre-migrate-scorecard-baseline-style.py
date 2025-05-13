from odoo.upgrade.util.spreadsheet import iter_commands


def migrate(cr, version):
    chart_editing_cmds = ["CREATE_CHART", "UPDATE_CHART"]
    for commands in iter_commands(cr, like_any=["%{}%".format(cmd.replace("_", r"\_")) for cmd in chart_editing_cmds]):
        for command in commands:
            if command["type"] in chart_editing_cmds and "baselineDescr" in command.get("definition", {}):
                command["definition"]["baselineDescr"] = {"text": command["definition"]["baselineDescr"]}
