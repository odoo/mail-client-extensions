# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute("ALTER TABLE barcode_rule ALTER COLUMN pattern TYPE varchar")
    cr.execute("ALTER TABLE barcode_rule ALTER COLUMN alias TYPE varchar")
