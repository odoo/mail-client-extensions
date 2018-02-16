# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    cr.execute("""
        SELECT company_id
          FROM account_journal
         WHERE "type" = 'general'
      GROUP BY company_id
    """)
    cids = [c[0] for c in cr.fetchall()]
    for company in util.env(cr)['res.company'].browse(cids):
        company.create_op_move_if_non_existant()
