# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute("ALTER TABLE calendar_appointment_slot ALTER COLUMN weekday TYPE varchar")
