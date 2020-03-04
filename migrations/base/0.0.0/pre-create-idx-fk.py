# -*- coding: utf-8 -*-
import logging
import os

from odoo.addons.base.maintenance.migrations import util

NS = "odoo.addons.base.maintenance.migrations.base."
_logger = logging.getLogger(NS + __name__)


def migrate(cr, version):

    min_rows = int(os.environ.get("ODOO_MIG_CREATE_FK_INDEX_MIN_ROWS", "40000"))
    if min_rows == 0:
        _logger.info("ODOO_MIG_CREATE_FK_INDEX_MIN_ROWS is set to 0, Index creation skipped")
        return

    cr.execute(
        """
        WITH big_tables AS(
        -- RETRIEVE BIG TABLES
            SELECT reltuples approximate_row_count , relname relation_name
            FROM pg_class pg_c
            JOIN pg_namespace pg_n ON pg_n.oid = pg_c.relnamespace
            WHERE pg_n.nspname = 'public' -- only use the public schema
            AND pg_c.relkind = 'r' -- only select the tables
            AND reltuples >= %s -- arbitrary number saying this is a big table
        )
        -- FIND foreign KEYS
            SELECT
                quote_ident
                (concat
                    (
                    'upgrade_fk_related_idx_',
                    ROW_NUMBER() OVER(ORDER BY tc.constraint_name )::varchar
                    )
                )AS index_name,
                quote_ident(tc.table_name),
                quote_ident(kcu.column_name)
            FROM
                information_schema.table_constraints AS tc
                JOIN information_schema.key_column_usage AS kcu ON tc.constraint_name = kcu.constraint_name AND tc.table_schema = kcu.table_schema
                JOIN information_schema.constraint_column_usage AS ccu ON ccu.constraint_name = tc.constraint_name AND ccu.table_schema = tc.table_schema
                LEFT JOIN big_tables bt1 ON bt1.relation_name = tc.table_name
            WHERE constraint_type = 'FOREIGN KEY' AND kcu.column_name NOT IN ('write_uid','create_uid')
            AND (bt1.relation_name IS NOT NULL)
            AND NOT EXISTS
            (
                    -- FIND EXISTING INDEXES
                    SELECT 1
                    FROM (select *, unnest(indkey) as unnest_indkey from pg_index) x
                    JOIN pg_class c ON c.oid = x.indrelid
                    JOIN pg_class i ON i.oid = x.indexrelid
                    JOIN pg_attribute a ON (a.attrelid=c.oid AND a.attnum=x.unnest_indkey)
                    WHERE (c.relkind = ANY (ARRAY['r'::"char", 'm'::"char"]))
                    AND i.relkind = 'i'::"char"
                    AND c.relname = tc.table_name
                    GROUP BY i.relname, x.indisunique, x.indisprimary
                    HAVING array_agg(a.attname::text ) = ARRAY[kcu.column_name::text]
            )
            ORDER BY 2,3
        """,
        [min_rows],
    )
    if cr.rowcount:
        create_index_queries = []
        util.ENVIRON["__created_fk_idx"] = []
        for index_name, table_name, column_name in cr.fetchall():
            util.ENVIRON["__created_fk_idx"].append(index_name)
            create_index_queries.append("CREATE INDEX %s ON %s(%s)" % (index_name, table_name, column_name))
        _logger.info("creating %s indexes (might be slow)", len(create_index_queries))
        util.parallel_execute(cr, create_index_queries)
