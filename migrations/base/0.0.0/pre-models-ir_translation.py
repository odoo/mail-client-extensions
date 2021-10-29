from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    query = """
        UPDATE ir_translation
           SET state = NULL
         WHERE state = 'false'
    """
    util.parallel_execute(cr, util.explode_query(cr, query))
