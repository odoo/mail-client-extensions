# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # Easier to let the ORM to recreate the whole table instead of droping the bunch of
    # boolean fields that have been converted to 0/1 selection fields.
    cr.execute("DROP TABLE purchase_config_settings")

    util.remove_view(cr, 'purchase.view_purchase_config')
    util.remove_view(cr, 'purchase.purchase_order_2_stock_picking')
    util.remove_view(cr, 'purchase.view_product_normal_purchase_buttons_from')
    util.remove_view(cr, 'purchase.purchase_order_line_form')
    
    # po_line tax relation table uses the standard table & columns names from now on
    cr.execute("""
        ALTER TABLE purchase_order_taxe RENAME COLUMN ord_id TO purchase_order_line_id
    """)
    cr.execute("""
        ALTER TABLE purchase_order_taxe RENAME COLUMN tax_id TO account_tax_id
    """)
    cr.execute("""
        ALTER TABLE purchase_order_taxe RENAME TO account_tax_purchase_order_line_rel
        """)
    # old to new state mapping
    cr.execute("""
        UPDATE purchase_order
            SET state = CASE
                WHEN  state IN ('confirmed', 'approved', 'except_picking', 'except_invoice') THEN 'purchase'
                WHEN state = 'bid' THEN 'to approve'
                ELSE state
            END
        """)

    # the state field of purchase.order.line should have been stored, but a typo in the code prevented that
    # I'll do the migration as intended since we'll fix this is saas-7 (probably)
    # and we might be happy to have kept this info
    cr.execute("UPDATE purchase_order_line SET state=po.state FROM purchase_order AS po WHERE po.id=order_id")  # field is now related