from odoo.upgrade.util.spreadsheet import iter_commands


def migrate(cr, version):
    cr.execute("SELECT code, week_start FROM res_lang")
    week_starts = dict(cr.fetchall())
    for commands in iter_commands(cr, like_all=[r"%UPDATE\_LOCALE%"]):
        for command in commands:
            if command["type"] != "UPDATE_LOCALE":
                continue
            command["locale"]["weekStart"] = int(week_starts.get(command["locale"]["code"], 1))
