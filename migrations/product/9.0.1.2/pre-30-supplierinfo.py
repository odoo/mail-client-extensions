# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    cr.execute("""DELETE FROM product_supplierinfo i
                   WHERE NOT EXISTS(SELECT 1 FROM pricelist_partnerinfo WHERE suppinfo_id=i.id)
               """)
    util.create_column(cr, 'product_supplierinfo', 'price', 'numeric')
    util.create_column(cr, 'product_supplierinfo', 'currency_id', 'int4')

    columns, i_columns = util.get_columns(cr, 'product_supplierinfo',
                                          ('id', 'price', 'min_qty'), ['i'])
    updated_si = set()
    cr.execute("SELECT suppinfo_id, price, min_quantity FROM pricelist_partnerinfo")
    for sid, price, qty in cr.fetchall():
        if sid in updated_si:
            cr.execute("""INSERT INTO product_supplierinfo({columns}, price, min_qty)
                               SELECT {i_columns}, %s, %s
                                 FROM product_supplierinfo i
                                WHERE i.id=%s
                       """.format(columns=','.join(columns), i_columns=','.join(i_columns)),
                       [price, qty, sid])
        else:
            updated_si.add(sid)
            cr.execute("UPDATE product_supplierinfo SET price=%s, min_qty=%s WHERE id=%s",
                       [price, qty, sid])

    # set currency to the coalesce(company of self, company of template, main company)
    cr.execute("""
        UPDATE product_supplierinfo i
           SET currency_id=(SELECT currency_id
                              FROM res_company
                             WHERE id=COALESCE(i.company_id, t.company_id, %s))
          FROM product_template t
         WHERE t.id = i.product_tmpl_id
    """, [util.ref(cr, 'base.main_company')])
