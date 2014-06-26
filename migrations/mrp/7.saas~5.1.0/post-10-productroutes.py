# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util
from openerp import SUPERUSER_ID
from openerp.modules.registry import RegistryManager


def migrate(cr, version):
    """
        Need to link mrp routes to products that had produce as procure method
    """
    registry = RegistryManager.get(cr.dbname)
    mod_obj = registry['ir.model.data']
    mrp_route = mod_obj.xmlid_to_res_id(cr, SUPERUSER_ID, 'mrp.route_warehouse0_manufacture')
    cr.execute("""
    INSERT INTO stock_route_product (product_id, route_id)
    select id, %s from product_template where supply_method = 'produce'
    """, (mrp_route,))
    
    
    # Fields that moved from product_product to product_template
    cr.execute("""
        UPDATE product_template SET track_production = pp.track_production, produce_delay = pp.produce_delay
        FROM product_product pp WHERE product_template.id = pp.product_tmpl_id 
    """)