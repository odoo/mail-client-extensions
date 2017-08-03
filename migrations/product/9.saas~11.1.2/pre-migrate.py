# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.rename_xmlid(cr, 'product.product_template_action_product',
                      'product.product_template_action_all')

    # column change type: remove it to let the ORM recreate it correctly
    cr.execute("ALTER TABLE base_config_settings DROP COLUMN IF EXISTS group_product_variant")
