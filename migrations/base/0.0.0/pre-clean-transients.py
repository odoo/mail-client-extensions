# -*- coding: utf-8 -*-
import psycopg2

from odoo.tools import ignore
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute("SELECT model FROM ir_model WHERE transient = true")
    models = cr.fetchall()

    if util.parse_version(version) >= util.parse_version("10.saas~15"):
        # Before saas~15, we cannot ensure that there is no Model that link to a TramsientModel
        # See odoo/odoo@f8e573db2350b025afec8407eeb5849c7a31afa4
        tables = ", ".join(util.table_of_model(cr, model) for model, in models)
        cr.execute("TRUNCATE {} CASCADE".format(tables))
    else:
        for (model,) in models:
            with ignore(psycopg2.Error), util.savepoint(cr):
                cr.execute("DELETE FROM " + util.table_of_model(cr, model))

    for ir in util.indirect_references(cr, bound_only=True):
        query = 'DELETE FROM "{0}" WHERE {1} AND "{2}" IS NOT NULL'.format(ir.table, ir.model_filter(), ir.res_id)
        with ignore(psycopg2.Error), util.savepoint(cr):
            cr.executemany(query, models)
