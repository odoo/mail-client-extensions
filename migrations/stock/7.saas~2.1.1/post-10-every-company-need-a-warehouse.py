# -*- coding: utf-8 -*-
from openerp import SUPERUSER_ID
from openerp.modules.registry import RegistryManager

def migrate(cr, version):
    # NOTE: customers don't understand why we create useless warehouses for
    #       companies they might only use for accounting. On the other hand, we
    #       don't really remember why we did this script.
    return

    # Ensure every company have a warehouse
    registry = RegistryManager.get(cr.dbname)
    Warehouse = registry['stock.warehouse']

    cr.execute("""SELECT id, name, partner_id
                    FROM res_company c
                   WHERE NOT EXISTS(SELECT id
                                      FROM stock_warehouse
                                     WHERE company_id = c.id)
               """)

    for company_id, name, partner_id in cr.fetchall():
        Warehouse.create(cr, SUPERUSER_ID, {
            'name': name,
            'code': name[0:3].upper(),
            'company_id': company_id,
            'partner_id': partner_id,
        })
