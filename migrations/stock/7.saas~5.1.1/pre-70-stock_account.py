# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # as stock_account is a new module, no migration script will be executed, do it here
    xids = """
        stock_journal_sequence
        stock_journal
        group_inventory_valuation
        group_stock_inventory_valuation
    """.split()
    for x in xids:
        util.rename_xmlid(cr, 'stock.' + x, 'stock_account.' + x)

    util.convert_field_to_property(
        cr, 'product.template', 'cost_method', 'char', default_value='standard',
        default_value_ref='stock_account.default_cost_method',
    )
    util.move_field_to_module(cr, 'product.template', 'cost_method', 'product', 'stock_account')

    util.convert_field_to_property(
        cr, 'product.product', 'valuation', 'char', default_value='manual_periodic',
        default_value_ref='stock_account.default_valuation',
        company_field='SELECT company_id FROM product_template WHERE id=t.product_tmpl_id',
    )
    util.move_field_to_module(cr, 'product.product', 'valuation', 'stock', 'stock_account')

    # users in group "product.group_costing_method" must be in group
    # "stock_account.group_inventory_valuation"
    gp_cm = util.ref(cr, 'product.group_costing_method')
    gp_iv = util.ref(cr, 'stock_account.group_inventory_valuation')
    if gp_cm and gp_iv:
        cr.execute("""UPDATE res_groups_users_rel r
                         SET gid = %s
                       WHERE gid = %s
                         AND NOT EXISTS (SELECT 1
                                           FROM res_groups_users_rel
                                          WHERE gid = %s
                                            AND uid = r.uid)
                   """, (gp_iv, gp_cm, gp_iv))
        cr.execute("DELETE FROM res_groups_users_rel WHERE gid=%s", (gp_cm,))
