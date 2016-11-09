# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def field(cr, model, name):
    cr.execute("""
        SELECT id
          FROM ir_model_fields
         WHERE model=%s
           AND name=%s
    """, [model, name])
    return (cr.fetchone() or [None])[0]

def migrate(cr, version):
    src_field = field(cr, 'sale.subscription', 'template_asset_category_id')
    dst_field = field(cr, 'sale.subscription.template', 'template_asset_category_id')

    cr.execute("UPDATE ir_property SET fields_id=%s WHERE fields_id=%s", [dst_field, src_field])
    cr.execute("""
        UPDATE ir_property p
           SET res_id='sale.subscription.template,' || t.id
          FROM sale_subscription_template t
         WHERE p.type = 'many2one'
           AND p.fields_id = %s
           AND p.res_id = 'sale.subscription,' || t._sss_id
    """, [dst_field])

    util.remove_field(cr, 'sale.subscription', 'template_asset_category_id')
    util.remove_column(cr, 'sale_subscription_template', '_sss_id')
