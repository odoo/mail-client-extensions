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
    buy_route = mod_obj.xmlid_to_res_id(cr, SUPERUSER_ID, 'purchase.route_warehouse0_buy')
    cr.execute("""
    INSERT INTO stock_route_product (product_id, route_id)
    select id, %s from product_template where supply_method = 'buy'
    """, (buy_route,))

    wh_obj = registry['stock.warehouse']
    whs = wh_obj.search(cr, SUPERUSER_ID, [])
    wh_obj.write(cr, SUPERUSER_ID, whs, {'buy_to_resupply': True})