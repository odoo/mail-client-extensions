from odoo.upgrade.util.spreadsheet import iter_commands


def migrate(cr, version):
    for commands in iter_commands(cr, like_any=[r"%CREATE\_CHART%", r"%UPDATE\_CHART%"]):
        for command in commands:
            if command["type"] not in ("CREATE_CHART", "UPDATE_CHART"):
                continue
            definition = command["definition"]
            if not definition["type"].startswith("odoo_"):
                continue
            cumulated_start = definition.get("cumulatedStart", definition.get("cumulative", False))
            definition["cumulatedStart"] = cumulated_start
            if "metaData" in definition:
                definition["metaData"]["cumulatedStart"] = cumulated_start
