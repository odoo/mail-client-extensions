# -*- coding: utf-8 -*-
from openerp import SUPERUSER_ID
from openerp.modules.registry import RegistryManager
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    """
        Link mto route with products that had route MTO
    """
    registry = RegistryManager.get(cr.dbname)
    mod_obj = registry['ir.model.data']
    mto_route = mod_obj.xmlid_to_res_id(cr, SUPERUSER_ID, 'stock.route_warehouse0_mto')
    cr.execute("""
    INSERT INTO stock_route_product (product_id, route_id)
    select id, %s from product_template where procure_method = 'make_to_order' 
    """, (mto_route,))