import logging

from psycopg2 import sql

from odoo.addons.base.maintenance.migrations import util

_logger = logging.getLogger("odoo.upgrade.base.000.{}".format(__name__))


def migrate(cr, version):
    models = ["ir.actions.actions"] + [
        inh.model for inh in util.for_each_inherit(cr, "ir.actions.actions") if not inh.via
    ]

    # These columns have constraints that collide with a null value and are supposed to cascade on delete
    removable_refs = [
        ("ir_filters", "action_id"),
        ("studio_approval_rule", "action_id"),
    ]

    cr.execute(
        """
        SELECT model, name, required
          FROM ir_model_fields
         WHERE ttype = 'many2one'
           AND relation IN %s
           AND store IS TRUE
        """,
        [tuple(models)],
    )
    for model, column, required in cr.fetchall():
        table = util.table_of_model(cr, model)
        if not util.column_updatable(cr, table, column):
            continue
        if required or (table, column) in removable_refs:
            query = util.format_query(
                cr,
                """
                SELECT array_agg(t.id)
                  FROM {} t
                 WHERE NOT EXISTS(
                    SELECT 1 FROM ir_actions a WHERE a.id = t.{}
                 )
                   AND t.{} IS NOT NULL
                """,
                table,
                column,
                column,
            )
            cr.execute(query)
            ids = cr.fetchone()[0]
            if ids:
                _logger.info("remove records %s(%r)", model, ids)
                util.remove_records(cr, model, ids)
        else:
            # we can just NULLify the field
            query = util.format_query(
                cr,
                """
                UPDATE {table} t
                   SET {column} = NULL
                 WHERE {column} IS NOT NULL
                   AND NOT EXISTS(
                    SELECT 1 FROM ir_actions a WHERE a.id = t.{column}
                   )
                """,
                table=table,
                column=column,
            )
            util.explode_execute(cr, query, table=table, alias="t")

    cr.execute(
        """
        SELECT model, name, required
          FROM ir_model_fields
         WHERE ttype = 'reference'
           AND store IS TRUE
        """
    )
    for model, column, required in cr.fetchall():
        table = util.table_of_model(cr, model)
        if not util.column_updatable(cr, table, column):
            continue
        if required:
            query = util.format_query(
                cr,
                """
                SELECT array_agg(t.id)
                  FROM {table} t
                 WHERE t.{column} LIKE ANY(%s)
                   AND NOT EXISTS(
                    SELECT 1 FROM ir_actions a WHERE a.id = SPLIT_PART(t.{column}, ',', 2)::int
                 )
                """,
                table=table,
                column=column,
            )
            cr.execute(query, [["{},%".format(m.replace("_", r"\_")) for m in models]])
            ids = cr.fetchone()[0]
            if ids:
                _logger.info("remove records %s(%r)", model, ids)
                util.remove_records(cr, model, ids)
        else:
            # we can just NULLify the field
            query0 = util.format_query(
                cr,
                """
                UPDATE {table} t
                   SET {column} = NULL
                 WHERE t.{column} LIKE ANY(%s)
                   AND NOT EXISTS(
                    SELECT 1 FROM ir_actions a WHERE a.id = SPLIT_PART(t.{column}, ',', 2)::int
                 )
                """,
                table=table,
                column=column,
            )
            query = cr.mogrify(query0, [["{},%".format(m.replace("_", r"\_")) for m in models]]).decode()
            util.explode_execute(cr, query, table=table, alias="t")

    for ir in util.indirect_references(cr, bound_only=True):
        if not ir.company_dependent_comodel:
            query = util.format_query(
                cr,
                """
                SELECT array_agg(t.id)
                  FROM {} t
                 WHERE ({})
                   AND NOT EXISTS(
                        SELECT 1 FROM ir_actions a WHERE a.id = t.{}
                   )
                """,
                ir.table,
                sql.SQL(ir.model_filter(prefix="t")),
                ir.res_id,
            )
            ids = []
            for model in models:
                cr.execute(query, [model])
                ids += cr.fetchone()[0] or []
            if ids:
                model = util.model_of_table(cr, ir.table)
                _logger.info("remove records %s(%r)", model, ids)
                util.remove_records(cr, model, ids)

        elif ir.company_dependent_comodel in models:
            # TODO
            pass

    if util.table_exists(cr, "ir_translation"):
        cr.execute(
            """
                DELETE
                  FROM ir_translation t
                 WHERE t.name LIKE ANY(%s)
                   AND NOT EXISTS(
                    SELECT 1 FROM ir_actions a WHERE a.id = t.res_id
                   )
            """,
            [["{},%".format(m.replace("_", r"\_")) for m in models]],
        )
