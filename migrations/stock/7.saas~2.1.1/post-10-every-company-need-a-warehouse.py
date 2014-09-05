# -*- coding: utf-8 -*-
from openerp import SUPERUSER_ID
from openerp.modules.registry import RegistryManager

def migrate(cr, version):
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
            'code': name,
            'company_id': company_id,
            'partner_id': partner_id,
        })
