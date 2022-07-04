# -*- coding: utf-8 -*-
import itertools
import logging

_logger = logging.getLogger("odoo.addons.base.maintenance.migrations.base." + __name__)


def migrate(cr, version):
    std_notnullable_fields = [
        # (Model, field),
        ("google_drive_config", "model_id"),
        ("ir_model_relation", "model"),
        ("ir_model_constraint", "model"),
        ("marketing_campaign", "model_id"),
        ("sms_template", "model_id"),
        ("test_new_api_creativework_edition", "res_model_id"),
    ]
    cr.execute(
        """
with fks as (SELECT (cl1.relname) as table,
                  (att1.attname) as column,
                  (con.conname) as conname,
                  con.confdeltype
             FROM pg_constraint as con, pg_class as cl1, pg_class as cl2,
                  pg_attribute as att1, pg_attribute as att2
            WHERE con.conrelid = cl1.oid
              AND con.confrelid = cl2.oid
              AND array_lower(con.conkey, 1) = 1
              AND con.conkey[1] = att1.attnum
              AND att1.attrelid = cl1.oid
              AND cl2.relname = 'ir_model'
              AND att2.attname = 'id'
              AND array_lower(con.confkey, 1) = 1
              AND con.confkey[1] = att2.attnum
              AND att2.attrelid = cl2.oid
              AND con.contype = 'f'
)
        SELECT c.relname, a.attname, conname, confdeltype, (a.attnotnull OR t.typnotnull)
          FROM pg_attribute a
          JOIN (pg_class c JOIN pg_namespace nc ON c.relnamespace = nc.oid) ON a.attrelid = c.oid
          JOIN (pg_type t JOIN pg_namespace nt ON t.typnamespace = nt.oid) ON a.atttypid = t.oid
          JOIN fks ON c.relname = fks.table AND a.attname = fks.column
         WHERE fks.confdeltype != 'c'
           AND NOT (%s)
    """
        % "OR".join(itertools.repeat("(c.relname=%s AND a.attname=%s)", len(std_notnullable_fields))),
        [param for param in itertools.chain.from_iterable(std_notnullable_fields)],
    )
    for table, column, conname, confdeltype, notnull in cr.fetchall():
        tail = " on column {}.{} because it's linked to `ir.model` model".format(table, column)
        if notnull:
            # If field is not on delete cascade, ensure it permit null values...
            cr.execute('ALTER TABLE "{table}" ALTER COLUMN "{column}" DROP NOT NULL'.format(table=table, column=column))
            _logger.warning("Permit NULL values %s", tail)
        if confdeltype == "r":
            cr.execute(
                """
                ALTER TABLE "{table}" DROP CONSTRAINT "{conname}";
                ALTER TABLE "{table}" ADD CONSTRAINT "{conname}" FOREIGN KEY ("{column}") references ir_model(id) ON DELETE SET NULL
                """.format(
                    table=table, column=column, conname=conname
                )
            )
            _logger.warning("Change 'ON DELETE RESTRICT' to 'ON DELETE SET NULL' %s", tail)
