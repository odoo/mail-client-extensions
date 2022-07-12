# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    cr.execute("UPDATE product_template SET uom_po_id=uom_id WHERE uom_po_id IS NULL")

    util.create_column(cr, 'product_supplierinfo', 'price', 'numeric')
    util.create_column(cr, 'product_supplierinfo', 'currency_id', 'int4')

    columns = util.get_columns(cr, 'product_supplierinfo', ('id', 'price', 'min_qty'))
    i_columns = ["i." + c for c in columns]
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

    # for the one without pricelist_partnerinfo, get the standard price from product
    cr.execute("""
        SELECT id FROM ir_model_fields WHERE model='product.template' AND name='standard_price'
    """)
    [fields_id] = cr.fetchone()
    cr.execute("""
        UPDATE product_supplierinfo i
           SET price = p.value_float * uom.factor / uom_po.factor
          FROM ir_property p, product_template t, product_uom uom, product_uom uom_po
         WHERE t.id = i.product_tmpl_id
           AND uom.id = t.uom_id
           AND uom_po.id = t.uom_po_id
           AND p.fields_id = %s
           AND p.company_id = coalesce(i.company_id, t.company_id)
           AND p.res_id = 'product.template,' || t.id
           AND i.price IS NULL
    """, [fields_id])
    # check for all-companies properties
    cr.execute("""
        UPDATE product_supplierinfo i
           SET price = p.value_float * uom.factor / uom_po.factor
          FROM ir_property p, product_template t, product_uom uom, product_uom uom_po
         WHERE t.id = i.product_tmpl_id
           AND uom.id = t.uom_id
           AND uom_po.id = t.uom_po_id
           AND p.fields_id = %s
           AND p.company_id IS NULL
           AND p.res_id = 'product.template,' || i.product_tmpl_id
           AND i.price IS NULL
    """, [fields_id])

    # Due to default values, company_id of supplier info should not be NULL
    # In case, no property exists for this product template, we simply fallback to lst_price
    cr.execute("""
        UPDATE product_supplierinfo i
           SET price = coalesce(t.list_price, 0) * uom.factor / uom_po.factor
          FROM product_template t, product_uom uom, product_uom uom_po
         WHERE t.id = i.product_tmpl_id
           AND uom.id = t.uom_id
           AND uom_po.id = t.uom_po_id
           AND i.price IS NULL
    """)

    # set currency to the coalesce(company of self, company of template, main company)
    cr.execute("""
        UPDATE product_supplierinfo i
           SET currency_id=(SELECT currency_id
                              FROM res_company
                             WHERE id=COALESCE(i.company_id, t.company_id, %s))
          FROM product_template t
         WHERE t.id = i.product_tmpl_id
    """, [util.ref(cr, 'base.main_company')])
