import itertools
from collections import defaultdict

from psycopg2 import sql

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
        for fk_table, fk_column, fk_constraint, deltype in util.get_fk(cr, table, quote_ident=False):
            if deltype != "c":
                columns_to_set_null[fk_table].append(fk_column)
                fks_to_drop[fk_table].append(fk_constraint)

    if columns_to_set_null:
        queries = [
            util.format_query(
                cr,
                "ALTER TABLE {} {}",
                t,
                sql.SQL(", ").join(sql.SQL(util.format_query(cr, "ALTER COLUMN {} DROP NOT NULL", c)) for c in columns),
            )
            for t, columns in columns_to_set_null.items()
        ]
        util.parallel_execute(cr, queries)
        update_set_null_queries = list(
            itertools.chain.from_iterable(
                util.explode_query_range(
                    cr,
                    util.format_query(
                        cr,
                        "UPDATE {} SET {} WHERE ({}) AND {{parallel_filter}}",
                        t,
                        sql.SQL(", ").join(sql.SQL(util.format_query(cr, "{} = NULL", c)) for c in q),
                        sql.SQL(" OR ").join(sql.SQL(util.format_query(cr, "{} IS NOT NULL", c)) for c in q),
                    ),
                    table=t,
                )
                for t, q in columns_to_set_null.items()
            )
        )
        util.parallel_execute(cr, update_set_null_queries)

    for table_name, constraints in fks_to_drop.items():
        query = util.format_query(
            cr,
            "ALTER TABLE {} {}",
            table_name,
            sql.SQL(", ").join(sql.SQL(util.format_query(cr, "DROP CONSTRAINT {}", c)) for c in constraints),
        )
        cr.execute(query)
    cr.execute(util.format_query(cr, "TRUNCATE {} CASCADE", sql.SQL(", ").join(map(sql.Identifier, tables))))

    for ir in util.indirect_references(cr, bound_only=True):
        if ir.company_dependent_comodel:
            # XXX: company dependent references to transient models are not handled
            continue
        # The frontend may create attachments via oe-bordered-editor on new records with res_id=0
        # those attachments are referenced directly from html fields inline from their value
        res_id = util.format_query(cr, "NULLIF({}, 0)", ir.res_id) if ir.table == "ir_attachment" else ir.res_id
        query = util.format_query(cr, "DELETE FROM {} WHERE {} AND {} IS NOT NULL", ir.table, ir.model_filter(), res_id)
        util._logger.info("Cleaning references to transient models from %s", ir.table)
        util.parallel_execute(cr, [cr.mogrify(query, data).decode() for data in models])


def get_tables_of_models(cr, models):
    """Return the table names of the models from the list that have an associated table."""
    tables = []
    for (model,) in models:
        table_name = util.table_of_model(cr, model)
        if util.table_exists(cr, table_name):
            tables.append(table_name)
    return tables
