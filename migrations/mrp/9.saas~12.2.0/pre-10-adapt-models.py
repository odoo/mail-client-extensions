# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util
from openerp.addons.base.maintenance.migrations.util import MigrationError

def migrate(cr, version):
    
    cr.execute("""SELECT COUNT(*) FROM mrp_production WHERE state NOT IN ('done', 'cancel') LIMIT 1""")
    res = cr.fetchone()
    if res and res[0] > 0:
        raise MigrationError('The migration does not support open production orders for the moment. There are %s' % res)
    
    util.remove_view(cr, 'mrp.mrp_production_reorder_form_view')
    util.remove_view(cr, 'mrp.mrp_production_form_inherit_view')
    util.remove_view(cr, 'mrp.mrp_production_form_inherit_view2')

    # In case of mrp_operations, should also remove workflow on work orders
    util.drop_workflow(cr, 'mrp.production.workcenter.line')
    # In saas-11, mrp_workorder is a view in mrp_operation, while in saas-12 it is a new object
    util.delete_model(cr, 'mrp.workorder')
    util.rename_model(cr, 'mrp.production.workcenter.line', 'mrp.workorder')
    util.drop_workflow(cr, 'mrp.production')

    # Do not remove scheduled products table for the moment as it might be used to calculate unit_factor