# -*- coding: utf-8 -*-
from functools import partial
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    for f in 'company_currency_id amount_currency analytic_amount_currency'.split():
        util.remove_field(cr, 'account.analytic.line', f)

    util.create_column(cr, 'account_payment_term_line', 'day_of_the_month', 'int4')
    cr.execute("""
        UPDATE account_payment_term_line
           SET option = CASE WHEN option = 'fix_day_following_month'
                             THEN 'after_invoice_month'
                             WHEN option = 'last_day_following_month'
                             THEN 'day_following_month'
                             WHEN option = 'last_day_current_month'
                             THEN 'day_current_month'
                             ELSE option
                         END,
                days = CASE WHEN option IN ('last_day_following_month', 'last_day_current_month')
                            THEN 31
                            ELSE days
                        END
    """)

    # TODO search reversed moves

    util.remove_field(cr, 'res.company', 'accounts_code_digits')
    util.create_column(cr, 'res_company', 'account_sale_tax_id', 'int4')
    util.create_column(cr, 'res_company', 'account_purchase_tax_id', 'int4')
    env = util.env(cr)
    IrDef = env['ir.default']

    def get_default(c, f):
        value = IrDef.get('product.template', f, company_id=c)
        if value:
            # verify that the record actually exist
            tax_id = value[0]
            cr.execute("SELECT id FROM account_tax WHERE id=%s", [tax_id])
            if cr.rowcount:
                return tax_id

    cr.execute("SELECT id FROM res_company")
    for cid, in cr.fetchall():
        cr.execute(
            "UPDATE res_company SET account_sale_tax_id=%s, account_purchase_tax_id=%s WHERE id=%s",
            [get_default(cid, 'taxes_id'), get_default(cid, 'supplier_taxes_id'), cid])

    get_field = partial(env['ir.model.fields']._get, 'product.template')
    IrDef.search([
        ('condition', '=', False),
        ('user_id', '=', False),
        ('field_id', 'in', [get_field('taxes_id').id, get_field('supplier_taxes_id').id]),
    ]).unlink()

    util.remove_field(cr, 'res.config.settings', 'default_sale_tax_id')
    util.remove_field(cr, 'res.config.settings', 'default_purchase_tax_id')
    # odoo/odoo@026979c278175de4fa27fba1843b5b9320894d3e
    util.remove_field(cr, 'res.config.settings', 'code_digits')
