# -*- coding: utf-8 -*-
import logging

from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    _logger = logging.getLogger(__name__)

    # with help from https://wiki.postgresql.org/wiki/Retrieve_primary_key_columns
    cr.execute(
        r"""
           SELECT SUBSTRING(pg_get_expr(d.adbin,0), 'nextval\(''([[:alpha:]][\w\$]*)''::regclass\)') as sequence_name,
                t.relname table_name
             FROM pg_attribute a
             JOIN pg_class t ON t.oid=a.attrelid AND t.relkind='r'
        FULL JOIN pg_attrdef d ON d.adrelid=a.attrelid AND a.attnum=d.adnum
             JOIN pg_index i ON a.attrelid=i.indrelid AND a.attnum=any(i.indkey)
            WHERE a.attname='id';
        """
    )
    for seq_name, table_name in cr.fetchall():
        if seq_name is None:
            util.create_id_sequence(cr, table=table_name)
            continue

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
