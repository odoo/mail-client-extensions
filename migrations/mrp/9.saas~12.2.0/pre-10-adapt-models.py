# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util
from openerp.addons.base.maintenance.migrations.util import MigrationError

def migrate(cr, version):
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
    
    # Date_planned on mrp_operation has been renamed
    util.move_field_to_module(cr, 'mrp.workorder', 'date_planned', 'mrp_operations', 'mrp')
    util.rename_field(cr, 'mrp.workorder', 'date_planned', 'date_planned_start')
    
    # As the product_efficiency field disappears on the BoM / BoM line, we incorporate it in the product_qty of the bom_line immediately
    cr.execute("""
        UPDATE mrp_bom_line bl
        SET product_qty = bl.product_qty / b.product_efficiency
        FROM mrp_bom b
        WHERE bl.bom_id = b.id AND b.product_efficiency != 1.0 AND b.product_efficiency > 0.0
    """)
    cr.execute("""
        UPDATE mrp_bom_line SET product_qty = product_qty / product_efficiency
        WHERE product_efficiency != 1.0 AND product_efficiency > 0.0
    """)