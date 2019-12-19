# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute("SELECT model FROM ir_model WHERE transient = true")
    models = cr.fetchall()
    for model, in models:
        cr.execute("DELETE FROM " + util.table_of_model(cr, model))
    for ir in util.indirect_references(cr, bound_only=True):
        query = 'DELETE FROM "{0}" WHERE {1}'.format(ir.table, ir.model_filter())
        cr.executemany(query, models)
