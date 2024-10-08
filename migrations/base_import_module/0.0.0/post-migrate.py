from odoo.addons.base.maintenance.migrations.util import version_gte

try:
    from odoo import modules
except ImportError:
    from openerp import modules


def migrate(cr, version):
    if version_gte("17.0"):
        cr.execute(
            """
            UPDATE ir_module_module
               SET module_type = 'official'
             WHERE module_type IS NULL
               AND name IN %s
            """,
            [tuple(modules.get_modules())],
        )
