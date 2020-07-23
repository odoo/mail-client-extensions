# -*- coding: utf-8 -*-
import psycopg2

from odoo.tools import ignore
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute("SELECT model FROM ir_model WHERE transient = true")
    models = cr.fetchall()

    # Before saas~15, we cannot ensure that there is no Model that link to a TramsientModel
    # See odoo/odoo@f8e573db2350b025afec8407eeb5849c7a31afa4
    tables = [util.table_of_model(cr, model) for model, in models]
    for table in tables:
        for fk_table, fk_column, fk_constraint, deltype in util.get_fk(cr, table):
            if deltype != "c":
                cr.execute("ALTER TABLE {} ALTER COLUMN {} DROP NOT NULL".format(fk_table, fk_column))
                cr.execute("UPDATE {} SET {} = NULL WHERE {} IS NOT NULL".format(fk_table, fk_column, fk_column))
                cr.execute("ALTER TABLE {} DROP CONSTRAINT {}".format(fk_table, fk_constraint))
    tables = ", ".join(tables)
    cr.execute("TRUNCATE {} CASCADE".format(tables))

    for ir in util.indirect_references(cr, bound_only=True):
        query = 'DELETE FROM "{0}" WHERE {1} AND "{2}" IS NOT NULL'.format(ir.table, ir.model_filter(), ir.res_id)
        with ignore(psycopg2.Error), util.savepoint(cr):
            cr.executemany(query, models)
