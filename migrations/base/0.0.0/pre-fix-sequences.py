# -*- coding: utf-8 -*-
import logging

from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    _logger = logging.getLogger(__name__)

    # with help from https://wiki.postgresql.org/wiki/Retrieve_primary_key_columns
    query = r"""
           SELECT SUBSTRING(pg_get_expr(d.adbin,0), 'nextval\(''([[:alpha:]][\w\$]*)''::regclass\)') as sequence_name,
                  t.relname table_name
             FROM pg_attribute a
             JOIN pg_type tt
               ON tt.oid=a.atttypid
              AND tt.typname='int4'
             JOIN pg_class t
               ON t.oid=a.attrelid
              AND t.relkind='r'
        FULL JOIN pg_attrdef d
               ON d.adrelid=a.attrelid
              AND a.attnum=d.adnum
             JOIN pg_index i
               ON a.attrelid=i.indrelid
              AND a.attnum=any(i.indkey)
             JOIN pg_namespace n
               ON t.relnamespace = n.oid
            WHERE a.attname='id'
              AND n.nspname=current_schema()
        """

    if cr._cnx.server_version >= 100000:
        # identity column have been introduced in pg 10.0, these must be
        # ignored as they already have their own implicit sequences.
        # zero bytes ('') attidentity means columns isn't identity
        query += " AND a.attidentity = ''"

    cr.execute(query)

    for seq_name, table_name in cr.fetchall():
        if seq_name is None:
            util.create_id_sequence(cr, table=table_name)
            continue

        cr.execute(util.format_query(cr, "SELECT max(id) FROM {}", table_name))
        max_id = cr.fetchone()[0]

        if not max_id:
            continue

        cr.execute(util.format_query(cr, "SELECT last_value FROM {}", seq_name))
        last_val = cr.fetchone()[0]

        if last_val >= max_id:
            continue

        _logger.info(
            "The sequence %s was inconsistent with the max id in table %s",
            seq_name,
            table_name,
        )
        cr.execute("SELECT setval(%s, %s)", [seq_name, max_id])
