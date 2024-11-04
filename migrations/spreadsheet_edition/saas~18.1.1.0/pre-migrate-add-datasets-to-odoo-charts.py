from odoo.upgrade.util.spreadsheet import iter_commands


def migrate(cr, version):
    for commands in iter_commands(cr, like_all=[r"%\_CHART%"]):
        for command in commands:
            if command["type"] not in ["CREATE_CHART", "UPDATE_CHART"]:
                continue
            definition = command["definition"]
            if "type" not in definition or not definition["type"].startswith("odoo"):
                continue

            trend = definition.get("trend")
            if trend:
                definition["dataSets"] = [{"trend": trend}]
                del definition["trend"]
            else:
                definition["dataSets"] = []
