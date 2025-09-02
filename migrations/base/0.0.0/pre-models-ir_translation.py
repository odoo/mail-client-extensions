from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.table_exists(cr, "ir_translation"):
        util.explode_execute(cr, "UPDATE ir_translation SET state = NULL WHERE state = 'false'", table="ir_translation")
