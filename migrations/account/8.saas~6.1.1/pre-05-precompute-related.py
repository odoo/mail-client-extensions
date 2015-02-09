# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'account_analytic_line', 'partner_id', 'int4')
    cr.execute("""UPDATE account_analytic_line l
                     SET partner_id = a.partner_id
                    FROM account_analytic_account a
                   WHERE a.id = l.account_id
               """)
