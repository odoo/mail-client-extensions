import logging

from odoo.addons.base.maintenance.migrations import util

_logger = logging.getLogger("odoo.addons.base.maintenance.migrations.base.0.0.0." + __name__)


def migrate(cr, version):
    pass


if util.version_gte("11.0"):
    from odoo.tools import sql

    origin_add_foreign_key = sql.add_foreign_key

    def add_foreign_key(cr, tablename1, columnname1, tablename2, columnname2, ondelete):
        if not util.column_exists(cr, tablename1, columnname1) or not util.column_exists(cr, tablename2, columnname2):
            _logger.error(
                "One of the table/field was missing %s.%s / %s.%s", tablename1, columnname1, tablename2, columnname2
            )
            return False
        allowed_cascade = util.ENVIRON["__fix_fk_allowed_cascade"]
        if ondelete in ("set null", "restrict") and util.column_nullable(cr, tablename1, columnname1):
            query = util.format_query(
                cr,
                """
                    UPDATE {t1} t
                       SET {c1} = NULL
                     WHERE {c1} IS NOT NULL
                       AND NOT EXISTS (SELECT {c2} FROM {t2} WHERE id=t.{c1})
                """,
                t1=tablename1,
                c1=columnname1,
                t2=tablename2,
                c2=columnname2,
            )
            rowcount = util.parallel_execute(cr, util.explode_query_range(cr, query, table=tablename1, alias="t"))
            if rowcount:
                _logger.warning(
                    "The value of the many2one column `%s` has been set to null for %s records of the table `%s` "
                    "because they referred to records that no longer exist (`%s` of `%s`), "
                    "and the foreign key is set as `ON DELETE SET NULL`.",
                    columnname1,
                    rowcount,
                    tablename1,
                    columnname2,
                    tablename2,
                )
        elif ondelete == "cascade" or (tablename1, columnname1) in allowed_cascade:
            # NOTE: deletes cannot be executed in parallel due to recusrive ON DELETE CASCADE constraints that can
            #       delete rows in another chunk, leading to concurrency errors.
            #       See discussion on https://github.com/odoo/upgrade/pull/3300
            query = util.format_query(
                cr,
                """
                    DELETE
                      FROM {t1} t
                     WHERE {c1} IS NOT NULL
                       AND NOT EXISTS (SELECT {c2} FROM {t2} WHERE id=t.{c1})
                """,
                t1=tablename1,
                c1=columnname1,
                t2=tablename2,
                c2=columnname2,
            )
            cr.execute(query)
            if cr.rowcount:
                _logger.warning(
                    "%s records of the table `%s` have been deleted "
                    "because the many2one column `%s` referred to records that no longer exist (`%s` of `%s`), "
                    "and the foreign key is set as `ON DELETE CASCADE`.",
                    cr.rowcount,
                    tablename1,
                    columnname1,
                    columnname2,
                    tablename2,
                )

        return origin_add_foreign_key(cr, tablename1, columnname1, tablename2, columnname2, ondelete)

    sql.add_foreign_key = add_foreign_key
