# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute("ALTER TABLE export_selection ALTER COLUMN value TYPE varchar")
    cr.execute("ALTER TABLE export_selection_withdefault ALTER COLUMN value TYPE varchar")
