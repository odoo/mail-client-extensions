from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if not util.table_exists(cr, "ir_translation"):
        return

    util.explode_execute(cr, "UPDATE ir_translation SET state = NULL WHERE state = 'false'", table="ir_translation")
