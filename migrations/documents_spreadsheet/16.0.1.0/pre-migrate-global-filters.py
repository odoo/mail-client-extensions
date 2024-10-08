from odoo.upgrade.util.spreadsheet import iter_commands


def migrate(cr, version):
    for commands in iter_commands(cr, like_all=[r"%\_GLOBAL\_FILTER%"]):
        for command in commands:
            if "_GLOBAL_FILTER" not in command["type"] or "filter" not in command:
                continue

            if command["filter"]["type"] == "date" and "year" in command["filter"]["defaultValue"]:
                default = command["filter"]["defaultValue"]
                if default["year"] == "this_year":
                    default["yearOffset"] = 0
                elif default["year"] == "last_year":
                    default["yearOffset"] = -1
                elif default["year"] == "antepenultimate_year":
                    default["yearOffset"] = -2
                del default["year"]
