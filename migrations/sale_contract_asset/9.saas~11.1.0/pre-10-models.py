# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):

    # new property `template_asset_category_id` which have to be initiated with value of
    # `asset_category_id` column. The easier way is to create a real field, fill it, then
    # use the funciton `util.convert_field_to_property`

    util.create_column(cr, 'sale_subscription', 'template_asset_category_id', 'int4')
    cr.execute("UPDATE sale_subscription SET template_asset_category_id = asset_category_id")

    # create the needed ir_model_field
    cr.execute("""
        INSERT INTO ir_model_fields(model, model_id, name, ttype, relation, state)
             VALUES ('sale.subscription',
                     (SELECT id FROM ir_model WHERE model='sale.subscription'),
                     'template_asset_category_id', 'many2one', 'account.asset.category', 'base')
    """)

    comp_query = 'SELECT company_id FROM account_analytic_account WHERE id=t.analytic_account_id'
    util.convert_field_to_property(cr, 'sale.subscription', 'template_asset_category_id',
                                   'many2one', 'account.asset.category', company_field=comp_query)
