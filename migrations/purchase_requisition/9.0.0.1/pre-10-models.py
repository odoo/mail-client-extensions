# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.drop_depending_views(cr, 'product_template', 'purchase_requisition')
    cr.execute("ALTER TABLE product_template RENAME COLUMN purchase_requisition TO _pr")
    util.create_column(cr, 'product_template', 'purchase_requisition', 'varchar')
    cr.execute("UPDATE product_template SET purchase_requisition = CASE WHEN _pr THEN 'tenders' ELSE 'rfq' END")
    cr.execute("ALTER TABLE product_template DROP COLUMN _pr")
