# -*- coding: utf-8 -*-
from operator import itemgetter
from openerp.addons.base.maintenance.migrations import util

def copy_columns(cr):
    # classic write fields
    cw_fields = util.splitlines("""
        uuid
        user_closable
        payment_method_id
        payment_mandatory
        plan_description
        user_selectable
        partial_invoice
    """)

    non_cw_fields = util.splitlines("""
        website_url
        recurring_mandatory_lines
        recurring_option_lines
        recurring_inactive_lines
        recurring_custom_lines
        recurring_amount_tax
        recurring_amount_total
        option_invoice_line_ids
    """)

    cr.execute("""
        SELECT *
          FROM ir_model
         WHERE model IN ('sale.subscription', 'account.analytic.account')
      ORDER BY model
    """)

    [old_model, new_model] = map(itemgetter(0), cr.fetchall())
    cr.execute("""
        UPDATE ir_model_fields
           SET model='sale.subscription', model_id=%s
         WHERE model_id=%s
           AND name IN %s
     RETURNING id
    """, [new_model, old_model, tuple(cw_fields + non_cw_fields)])

    fids = map(itemgetter(0), cr.fetchall())
    cr.execute("""
        UPDATE ir_model_data
           SET name='field_sale_subscription_' || substr(name, 32)
         WHERE model='ir.model.fields'
           AND res_id IN %s
    """, [tuple(fids)])

    for f in cw_fields:
        fdef = util.column_type(cr, 'account_analytic_account', f)
        util.create_column(cr, 'sale_subscription', f, fdef)

    set_values = ', '.join('{0} = a.{0}'.format(f) for f in cw_fields)

    cr.execute("""
        UPDATE sale_subscription s
           SET {0}
          FROM account_analytic_account a
         WHERE s.analytic_account_id = a.id
    """.format(set_values))

    for f in cw_fields:
        util.remove_column(cr, 'account_analytic_account', f)

def adapt_options(cr):
    cr.execute("""
        DELETE FROM account_analytic_invoice_line_option
              WHERE analytic_account_id NOT IN (SELECT analytic_account_id FROM sale_subscription)
    """)
    cr.execute("""
        ALTER TABLE account_analytic_invoice_line_option
    DROP CONSTRAINT IF EXISTS account_analytic_invoice_line_option_analytic_account_id_fkey
    """)

    util.rename_model(cr, 'account.analytic.invoice.line.option', 'sale.subscription.line.option')
    cr.execute("""
        UPDATE sale_subscription_line_option ssl
           SET analytic_account_id = sub.id
          FROM sale_subscription sub
         WHERE sub.analytic_account_id = ssl.analytic_account_id
    """)

def migrate(cr, version):
    # beside this is a new module, it has been tested on some databases that need to be migrated.
    # (ok, only our prod (and test) server only, actually)
    util.remove_record(cr, 'website_contract.access_account_portal')
    copy_columns(cr)
    adapt_options(cr)

    util.merge_module(cr, "website_quote_contract", "website_contract")
    if util.column_exists(cr, 'sale_quote_template', 'contract_template'):
        cr.execute("""
            UPDATE sale_quote_template
               SET contract_template = NULL
             WHERE contract_template NOT IN (SELECT analytic_account_id FROM sale_subscription)
        """)
        cr.execute("""
            ALTER TABLE sale_quote_template
        DROP CONSTRAINT IF EXISTS sale_quote_template_contract_template_fkey
        """)
        cr.execute("""
            UPDATE sale_quote_template t
               SET contract_template = s.id
              FROM sale_subscription s
             WHERE s.analytic_account_id = t.contract_template
        """)
