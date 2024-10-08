from odoo.upgrade.util.spreadsheet import iter_commands


def migrate(cr, version):
    for commands in iter_commands(cr, like_all=[r"%\_CHART%"]):
        for command in commands:
            if command["type"] not in ["CREATE_CHART", "UPDATE_CHART"]:
                continue
            definition = command["definition"]
            # 1. title is now an object
            if "title" in definition:
                definition["title"] = {"text": definition["title"]}
            # 2. dataSets is now an object
            if "dataSets" in definition:
                definition["dataSets"] = [{"dataRange": r} for r in definition.get("dataSets", [])]
