# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'res_partner', 'company_name', 'varchar')
    util.create_column(cr, 'res_partner', 'commercial_company_name', 'varchar')
    cr.execute("""
        UPDATE res_partner p
           SET commercial_company_name = CASE WHEN c.is_company THEN c.name
                                              ELSE p.company_name
                                          END
          FROM res_partner c
         WHERE c.id = p.commercial_partner_id
    """)
