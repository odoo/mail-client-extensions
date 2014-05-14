# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util
from openerp import SUPERUSER_ID
from openerp.modules.registry import RegistryManager


def migrate(cr, version):
    """
        Need to link buy routes to products that had buy as procure method
    """
    registry = RegistryManager.get(cr.dbname)
    mod_obj = registry['ir.model.data']
    mrp_route = mod_obj.xmlid_to_res_id(cr, SUPERUSER_ID, 'mrp.route_warehouse0_manufacture')
    cr.execute("""
    INSERT INTO stock_route_product (product_id, route_id)
    select id, %s from product_template where supply_method = 'produce'
    """, (mrp_route,))