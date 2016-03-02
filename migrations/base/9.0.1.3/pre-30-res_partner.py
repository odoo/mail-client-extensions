# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.rename_field(cr, 'res.partner.bank', 'bank', 'bank_id')
    util.rename_field(cr, 'res.partner.bank', 'state', 'acc_type')
    util.delete_model(cr, 'res.partner.bank.type')
    util.delete_model(cr, 'res.partner.bank.type.field')

    cr.execute("""
        UPDATE res_partner p
           SET name = concat(p.name, ' ', initcap(t.shortcut)),
               title = NULL
          FROM res_partner_title t
         WHERE p.title = t.id
           AND t.domain = 'partner'
    """)
    cr.execute("DELETE FROM res_partner_title WHERE domain='partner'")

    cr.execute("UPDATE res_partner SET type='contact' WHERE type='default'")
    cr.execute("""
        UPDATE res_partner
           SET type='other'
         WHERE type='contact'
           AND parent_id IS NOT NULL
           AND use_parent_address = false
           AND (street IS NOT NULL
             OR street2 IS NOT NULL
             OR zip IS NOT NULL
             OR city IS NOT NULL
             OR state_id IS NOT NULL
             OR country_id IS NOT NULL
           )
    """)

    util.create_column(cr, 'res_partner', 'company_type', 'varchar')
    cr.execute("""UPDATE res_partner
                     SET company_type = CASE WHEN is_company THEN 'company' ELSE 'person' END
               """)
