# -*- coding: utf-8 -*-

def migrate(cr, version):
    cr.execute("ALTER TABLE stock_production_lot DROP CONSTRAINT IF EXISTS name_ref_uniq")
