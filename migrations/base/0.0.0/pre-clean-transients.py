import itertools
from collections import defaultdict

import psycopg2
from psycopg2 import sql

try:
    from contextlib import suppress
except ImportError:
    from odoo.tools import ignore as suppress

from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute("SELECT model FROM ir_model WHERE transient = true")
    models = cr.fetchall()

    # Before saas~15, we cannot ensure that there is no Model that link to a TransientModel
    # See odoo/odoo@f8e573db2350b025afec8407eeb5849c7a31afa4
    tables = get_tables_of_models(cr, models)

    columns_to_set_null = defaultdict(list)
    fks_to_drop = defaultdict(list)
    for table in tables:
        for fk_table, fk_column, fk_constraint, deltype in util.get_fk(cr, table):
            if deltype != "c":
                columns_to_set_null[fk_table].append(fk_column)
                fks_to_drop[fk_table].append(fk_constraint)

    if columns_to_set_null:
        util.parallel_execute(
            cr,
            [
                "ALTER TABLE {} {}".format(t, ", ".join("ALTER COLUMN {} DROP NOT NULL".format(c) for c in columns))
                for t, columns in columns_to_set_null.items()
            ],
        )
        update_set_null_queries = list(
            itertools.chain.from_iterable(
                util.explode_query_range(
                    cr,
                    "UPDATE {} SET {} WHERE ({})".format(
                        t,
                        ", ".join("{} = NULL".format(c) for c in q),
                        " OR ".join("{} IS NOT NULL".format(c) for c in q),
                    ),
                    table=t,
                )
                for t, q in columns_to_set_null.items()
            )
        )
        util.parallel_execute(cr, update_set_null_queries)

    for table_name, constraints in fks_to_drop.items():
        cr.execute(
            "ALTER TABLE {} {}".format(table_name, ", ".join("DROP CONSTRAINT {}".format(c) for c in constraints))
        )
    cr.execute(util.format_query(cr, "TRUNCATE {} CASCADE", sql.SQL(", ").join(map(sql.Identifier, tables))))

    for ir in util.indirect_references(cr, bound_only=True):
        if ir.company_dependent_comodel:
            # XXX: company dependent references to transient models are not handled
            continue
        query = 'DELETE FROM "{}" WHERE {} AND "{}" IS NOT NULL'.format(ir.table, ir.model_filter(), ir.res_id)
        with suppress(psycopg2.Error), util.savepoint(cr):
            cr.executemany(query, models)


def get_tables_of_models(cr, models):
    """Return the table names of the models from the list that have an associated table."""
    tables = []
    for (model,) in models:
        table_name = util.table_of_model(cr, model)
        if util.table_exists(cr, table_name):
            tables.append(table_name)
    return tables
