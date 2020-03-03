# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute("UPDATE event_track_location SET name = 'Somewhere' WHERE name IS NULL")
