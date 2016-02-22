# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # create an empty template to satisfy the mandatory field after migration
    env = util.env(cr)

    cr.execute("""
        SELECT a.company_id, c.name
          FROM sale_subscription s
          JOIN account_analytic_account a ON (a.id = s.analytic_account_id)
          JOIN res_company c ON (c.id = a.company_id)
         WHERE s.template_id IS NULL
           AND s.type = 'contract'
      GROUP BY a.company_id, c.name
    """)
    for company_id, company_name in cr.fetchall():
        default = env['sale.subscription'].create({
            'type': 'template',
            'name': 'Default Template For %s' % company_name,
            'reference': 'DEF%02d' % company_id,
            'company_id': company_id,
            'state': 'open',
            'description': 'This empty template is here to enforce the mandatory template on subscriptions and was created automatically when you switched to Odoo 9. Feel free to replace it with something more meaningful to your business.'
        })
        cr.execute("""
            UPDATE sale_subscription s
               SET template_id = %s
              FROM account_analytic_account a
             WHERE a.id = s.analytic_account_id
               AND s.template_id IS NULL
               AND s.type = 'contract'
               AND a.company_id = %s
        """, [default.id, company_id])
