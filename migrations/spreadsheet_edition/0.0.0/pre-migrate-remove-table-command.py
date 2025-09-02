from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.util.spreadsheet import iter_commands


def migrate(cr, version):
    if util.version_between("saas~17.2", "19.0"):
        for commands in iter_commands(cr, like_all=[r"%REMOVE\_FILTER\_TABLE%"]):
            for command in commands:
                if command["type"] == "REMOVE_FILTER_TABLE":
                    command["type"] = "REMOVE_TABLE"
