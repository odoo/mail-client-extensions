# -*- coding: utf-8 -*-
  
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    pl_rule = util.ref(cr, 'product.product_pricelist_comp_rule')
    pl_item_rule = util.ref(cr, 'product.product_pricelist_item_comp_rule')
    cr.execute("UPDATE ir_rule SET active='f' WHERE id IN %s", [(pl_rule, pl_item_rule)])
