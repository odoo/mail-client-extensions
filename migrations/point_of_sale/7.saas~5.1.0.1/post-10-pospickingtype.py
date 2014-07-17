# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util
from openerp.modules.registry import RegistryManager
from openerp import SUPERUSER_ID

def migrate(cr, version):
    registry = RegistryManager.get(cr.dbname)
    mod_obj = registry['ir.model.data']
    result = mod_obj.xmlid_to_res_id(cr, SUPERUSER_ID, 'point_of_sale.picking_type_posout')
    if result:
        cr.execute("""
            UPDATE pos_config SET picking_type_id = %s
        """, (result,))