# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):

    util.move_field_to_module(cr, 'product.template', 'expense_policy', 'sale_expense', 'sale')
    util.create_column(cr, 'product_template', 'expense_policy', 'varchar')

    env = util.env(cr)
    if 'ir.values' in env:
        get_default = env['ir.values'].get_default
        set_default = env['ir.values'].set_default
    else:
        get_default = env['ir.default'].get
        get_default = env['ir.default'].set
    ip = get_default('product.template', 'invoice_policy')
    if ip == 'cost':
        set_default('product.template', 'invoice_policy', 'delivery')

    # NOTE: sql-fix for wrongly migrated databases:
    #  update product_template set expense_policy = 'no' where coalesce(can_be_expensed, false) = false and expense_policy != 'no';

    ep = "'no'"
    if util.column_exists(cr, 'product_template', 'can_be_expensed'):
        # FIXME handle databases < 9.0 (field renamed in 9.0)
        ep = "CASE WHEN can_be_expensed = true THEN 'cost' ELSE 'no' END"

    cr.execute("""
        UPDATE product_template
           SET expense_policy = {0},
               invoice_policy = 'delivery'
         WHERE invoice_policy = 'cost'
    """.format(ep))
    cr.execute("UPDATE product_template SET expense_policy = 'no' WHERE expense_policy IS NULL")

    # sale order line
    cr.execute("ALTER TABLE sale_order_line RENAME COLUMN price_reduce TO price_reduce_taxexcl")
    util.create_column(cr, 'sale_order_line', 'price_reduce', 'numeric')
    util.create_column(cr, 'sale_order_line', 'price_reduce_taxinc', 'numeric')
    cr.execute("""
        UPDATE sale_order_line
           SET price_reduce = COALESCE(price_unit, 0) * (1.0 - COALESCE(discount, 0) / 100.0),
               price_reduce_taxinc = CASE WHEN COALESCE(product_uom_qty, 0) = 0 THEN 0
                                          ELSE price_total / product_uom_qty
                                      END
    """)

    # account invoice
    util.create_column(cr, 'account_invoice', 'comment', 'text')
    util.create_column(cr, 'account_invoice', 'partner_shipping_id', 'int4')
    cr.execute("""
        UPDATE account_invoice i
           SET "comment" = c.sale_note
          FROM res_company c
         WHERE c.id = i.company_id
           AND i.comment is null
           AND i.type = 'out_invoice'
    """)
    cr.execute("UPDATE account_invoice SET partner_shipping_id = partner_id")
