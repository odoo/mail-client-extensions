# -*- coding: utf-8 -*-
import logging


def migrate(cr, version):
    _logger = logging.getLogger(__name__)

    # with help from https://wiki.postgresql.org/wiki/Retrieve_primary_key_columns
    cr.execute(
        r"""
        SELECT (regexp_matches(pg_get_expr(d.adbin,0),'nextval\(''([[:alpha:]][\w\$]*)''::regclass\)'))[1] seq_name,
               t.relname table_name
          FROM pg_attribute a
          JOIN pg_class t ON t.oid=a.attrelid AND t.relkind='r'
          JOIN pg_attrdef d ON d.adrelid=a.attrelid AND a.attnum=d.adnum
          JOIN pg_index i ON a.attrelid=i.indrelid AND a.attnum=any(i.indkey)
         WHERE a.attname='id'
           AND a.atthasdef
        """
    )
    for seq_name, table_name in cr.fetchall():
        cr.execute('SELECT max(id) FROM "{}"'.format(table_name))
        max_id = cr.fetchone()[0]

        if not max_id:
            continue

        cr.execute('SELECT last_value FROM "{}"'.format(seq_name))
        last_val = cr.fetchone()[0]

        if last_val >= max_id:
            continue

        _logger.info(
            "The sequence %s was inconsistent with the max id in table %s",
            seq_name,
            table_name,
        )
        cr.execute("SELECT setval('{}',%s)".format(seq_name), [max_id])
