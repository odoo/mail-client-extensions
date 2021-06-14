import logging

from odoo.addons.base.maintenance.migrations import util

_logger = logging.getLogger("odoo.addons.base.maintenance.migrations.base.0.0.0." + __name__)


def migrate(cr, version):
    util.ENVIRON["fix_fk_allowed_cascade"] = []


if util.version_gte("11.0"):
    import psycopg2

    from odoo.tools import sql

    origin_add_foreign_key = sql.add_foreign_key

    def add_foreign_key(cr, tablename1, columnname1, tablename2, columnname2, ondelete):
        try:
            with cr.savepoint():
                origin_add_foreign_key(cr, tablename1, columnname1, tablename2, columnname2, ondelete)
            # To limit the number of savepoints created per transaction
            cr.commit()
        except psycopg2.Error as e:
            if e.pgcode != "23503":
                raise

            kwargs = {
                "tablename1": tablename1,
                "columnname1": columnname1,
                "tablename2": tablename2,
                "columnname2": columnname2,
            }
            allowed_cascade = util.ENVIRON["fix_fk_allowed_cascade"]
            if ondelete in ("set null", "restrict") and util.column_nullable(cr, tablename1, columnname1):
                cr.execute(
                    """
                        UPDATE "%(tablename1)s" t
                        SET "%(columnname1)s" = NULL
                        WHERE NOT EXISTS (SELECT "%(columnname2)s" FROM "%(tablename2)s" WHERE id=t."%(columnname1)s")
                    """
                    % kwargs,
                )
                _logger.warning(
                    "The value of the many2one column `%s` has been set to null for %s records of the table `%s` "
                    "because they referred to records that no longer exist (`%s` of `%s`), "
                    "and the foreign key is set as `ON DELETE SET NULL`.",
                    columnname1,
                    cr.rowcount,
                    tablename1,
                    columnname2,
                    tablename2,
                )
            elif ondelete == "cascade" or (tablename1, columnname1) in allowed_cascade:
                cr.execute(
                    """
                        DELETE FROM "%(tablename1)s" t
                        WHERE NOT EXISTS (SELECT "%(columnname2)s" FROM "%(tablename2)s" WHERE id=t."%(columnname1)s")
                    """
                    % kwargs
                )
                _logger.warning(
                    "%s records of the table `%s` have been deleted "
                    "because the many2one column `%s` referred to records that longer exist (`%s` of `%s`), "
                    "and the foreign key is set as `ON DELETE CASCADE`.",
                    cr.rowcount,
                    tablename1,
                    columnname1,
                    columnname2,
                    tablename2,
                )
            else:
                raise

            origin_add_foreign_key(cr, tablename1, columnname1, tablename2, columnname2, ondelete)

    sql.add_foreign_key = add_foreign_key
