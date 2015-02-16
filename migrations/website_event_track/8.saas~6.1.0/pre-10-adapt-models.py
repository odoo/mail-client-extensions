# -*- coding: utf-8 -*-

def migrate(cr, version):
    # was an untyped related
    cr.execute("ALTER TABLE event_sponsor ALTER COLUMN sequence TYPE integer")
