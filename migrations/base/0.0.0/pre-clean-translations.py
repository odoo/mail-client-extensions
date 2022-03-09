# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute("DELETE FROM ir_translation WHERE value = src AND type IS DISTINCT FROM 'model'")
    cr.execute("DELETE FROM ir_translation WHERE value IS NULL")
    cr.execute("DELETE FROM ir_translation WHERE value = ''")
