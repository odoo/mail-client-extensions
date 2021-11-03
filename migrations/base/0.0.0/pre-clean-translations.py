# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute("DELETE FROM ir_translation WHERE value = src")
    cr.execute("DELETE FROM ir_translation WHERE value IS NULL")
    cr.execute("DELETE FROM ir_translation WHERE value = ''")
