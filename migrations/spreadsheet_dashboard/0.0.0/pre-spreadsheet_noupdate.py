from odoo import modules

from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.version_between("16.0", "saas~18.2"):
        cr.execute(
            """
            UPDATE ir_model_data
               SET noupdate = FALSE
             WHERE model = 'spreadsheet.dashboard'
               AND module IN %s
               AND noupdate = TRUE
            """,
            [tuple(modules.get_modules())],
        )
