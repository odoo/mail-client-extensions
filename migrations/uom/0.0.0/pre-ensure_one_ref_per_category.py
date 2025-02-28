from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.version_between("16.0", "18.0"):
        cr.execute(
            """
            UPDATE uom_uom
               SET uom_type = 'bigger',
                   factor = 1
             WHERE uom_type = 'reference'
               AND active IS NOT TRUE
            """
        )
