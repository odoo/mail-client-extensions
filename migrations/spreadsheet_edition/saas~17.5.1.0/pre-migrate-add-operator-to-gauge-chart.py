from odoo.upgrade.util.spreadsheet import iter_commands


def migrate(cr, version):
    for commands in iter_commands(cr, like_all=[r"%\_CHART%"]):
        for command in commands:
            if command["type"] not in ["CREATE_CHART", "UPDATE_CHART"]:
                continue
            definition = command["definition"]
            if "type" not in definition or definition["type"] != "gauge" or "sectionRule" not in definition:
                continue
            definition["sectionRule"]["lowerInflectionPoint"]["operator"] = "<="
            definition["sectionRule"]["upperInflectionPoint"]["operator"] = "<="
