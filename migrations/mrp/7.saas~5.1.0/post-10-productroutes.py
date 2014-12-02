# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util
from openerp import SUPERUSER_ID
from openerp.modules.registry import RegistryManager
from openerp.release import series

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
    
    #Changes to product_product 
    if series != '8.0':
        cr.execute("""UPDATE product_product SET produce_delay = pt.produce_delay
                    FROM product_template pt
                    WHERE pt.id = product_product.product_tmpl_id""")

    wh_obj = registry['stock.warehouse']
    whs = wh_obj.search(cr, SUPERUSER_ID, [])
    wh_obj.write(cr, SUPERUSER_ID, whs, {'manufacture_to_resupply': True})