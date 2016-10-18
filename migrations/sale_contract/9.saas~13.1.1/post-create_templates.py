# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    extra_cols = []
    if util.module_installed(cr, 'website_contract'):
        wc_cols = util.splitlines("""
            plan_description
            user_selectable
            user_closable
            payment_mandatory
            partial_invoice
        """)
        for col in wc_cols:
            ct = util.column_type(cr, 'sale_subscription', col)
            util.create_column(cr, 'sale_subscription_template', col, ct)
            extra_cols.append(col)
    else:
        # `plan_description` field is defined in `sale_contract` module. Even it does not appears
        # in any views by default, it may have been filled by the user and used in reports.
        # Check if we need to keep the information when creating templates.
        cr.execute("""
            SELECT count(1)
              FROM sale_subscription
             WHERE type='template'
               AND plan_description IS NOT NULL
        """)
        if cr.fetchone()[0]:
            col = 'plan_description'
            ct = util.column_type(cr, 'sale_subscription', col)
            util.create_column(cr, 'sale_subscription_template', col, ct)
            extra_cols.append(col)

    util.create_column(cr, 'sale_subscription_template', '_sss_id', 'int4')
    cr.execute("""
        INSERT INTO sale_subscription_template(
            _sss_id, name, active, code, description, recurring_rule_type, recurring_interval
            {extra}
        )
        SELECT s.id, a.name, a.active, a.code, s.description,
               s.recurring_rule_type, s.recurring_interval
               {s_extra}
          FROM sale_subscription s
          JOIN account_analytic_account a ON (a.id = s.analytic_account_id)
         WHERE s.type='template'
    """.format(extra=', '.join([''] + extra_cols),
               s_extra=', s.'.join([''] + extra_cols)))

    cr.execute("""
        INSERT INTO sale_subscription_template_line(
            product_id, name, subscription_template_id, uom_id, quantity
        )
        SELECT l.product_id, l.name, t.id, l.uom_id, l.quantity
          FROM sale_subscription_line l
          JOIN sale_subscription_template t
            ON (t._sss_id = l.analytic_account_id)
    """)

    # There is no ondelete=cascade on lines, delete them manually
    cr.execute("""
        DELETE FROM sale_subscription_line
              WHERE analytic_account_id IN (SELECT _sss_id FROM sale_subscription_template)
    """)

    if util.module_installed(cr, 'website_contract'):
        # XXX ideally this should be in a script in `website_contract` module
        util.rename_model(cr, 'sale.subscription.line.option', 'sale.subscription.template.option')
        util.create_column(cr, 'sale_subscription_template_option', 'subscription_template_id',
                           'int4')
        cr.execute("""
            UPDATE sale_subscription_template_option o
               SET subscription_template_id = t.id
              FROM sale_subscription_template t
             WHERE o.analytic_account_id = t._sss_id
        """)
        cr.execute("""
            DELETE FROM sale_subscription_template_option
                  WHERE subscription_template_id IS NULL
        """)
        util.remove_field(cr, 'sale.subscription.template.option', 'analytic_account_id')

    cr.execute("""
        UPDATE sale_subscription s
           SET template_id = t.id
          FROM sale_subscription_template t
         WHERE t._sss_id = s._tmpl_id
    """)

    # handle `website_contract` module
    for table in ['sale_order', 'sale_quote_template']:
        if util.column_exists(cr, table, 'contract_template'):
            cr.execute("ALTER TABLE {0} DROP CONSTRAINT {0}_contract_template_fkey".format(table))
            cr.execute("""
                UPDATE {0} o
                   SET contract_template = t.id
                  FROM sale_subscription_template t
                 WHERE o.contract_template = t._sss_id
            """.format(table))

    cr.execute("DELETE FROM sale_subscription WHERE type='template'")

    util.remove_field(cr, 'sale.subscription', 'type')
    for extra in extra_cols:
        util.remove_field(cr, 'sale.subscription', extra)

    # now related to template, delete column in db only
    util.remove_column(cr, 'sale_subscription', 'recurring_rule_type')
    util.remove_column(cr, 'sale_subscription', 'recurring_interval')

    # remove old columns...
    if not util.module_installed(cr, 'sale_contract_asset'):
        util.remove_column(cr, 'sale_subscription_template', '_sss_id')
    util.remove_column(cr, 'sale_subscription', '_tmpl_id')
