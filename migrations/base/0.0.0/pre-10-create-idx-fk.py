# -*- coding: utf-8 -*-
import logging

from odoo import api, models

from odoo.addons.base.maintenance.migrations import util

NS = "odoo.addons.base.maintenance.migrations.base."
_logger = logging.getLogger(NS + __name__)


def migrate(cr, version):
    create_index_queries = []
    util.ENVIRON["__created_fk_idx"] = []

    create_index_queries.append(
        "CREATE INDEX upg_attachment_cleanup_speedup_idx ON ir_attachment(res_model, res_field, id)"
    )
    util.ENVIRON["__created_fk_idx"].append("upg_attachment_cleanup_speedup_idx")

    # create indexes on `ir_model{,_fields}` to speed up models/fields deletion
    cr.execute(
        """
           SELECT quote_ident(concat('upgrade_fk_ir_model_idx_',
                                     ROW_NUMBER() OVER(ORDER BY con.conname)::varchar
                  )) AS index_name,
                  quote_ident(cl1.relname) as table,
                  quote_ident(att1.attname) as column
             FROM pg_constraint as con, pg_class as cl1, pg_class as cl2,
                  pg_attribute as att1, pg_attribute as att2
            WHERE con.conrelid = cl1.oid
              AND con.confrelid = cl2.oid
              AND array_lower(con.conkey, 1) = 1
              AND con.conkey[1] = att1.attnum
              AND att1.attrelid = cl1.oid
              AND cl2.relname IN ('ir_model', 'ir_model_fields')
              AND att2.attname = 'id'
              AND array_lower(con.confkey, 1) = 1
              AND con.confkey[1] = att2.attnum
              AND att2.attrelid = cl2.oid
              AND con.contype = 'f'
              AND NOT EXISTS (
                    -- FIND EXISTING INDEXES
                  SELECT 1
                    FROM (select *, unnest(indkey) as unnest_indkey from pg_index) x
                    JOIN pg_class c ON c.oid = x.indrelid
                    JOIN pg_class i ON i.oid = x.indexrelid
                    JOIN pg_attribute a ON (a.attrelid=c.oid AND a.attnum=x.unnest_indkey)
                   WHERE (c.relkind = ANY (ARRAY['r'::"char", 'm'::"char"]))
                     AND i.relkind = 'i'::"char"
                     AND c.relname = cl1.relname
                GROUP BY i.relname, x.indisunique, x.indisprimary
                 HAVING array_agg(a.attname::text) = ARRAY[att1.attname::text]
              )
        """
    )
    for index_name, table_name, column_name in cr.fetchall():
        util.ENVIRON["__created_fk_idx"].append(index_name)
        create_index_queries.append("CREATE INDEX %s ON %s(%s)" % (index_name, table_name, column_name))

    # now same for big tables
    cr.execute(
        """
        WITH big_tables AS(
        -- RETRIEVE BIG TABLES
            SELECT reltuples approximate_row_count , relname relation_name
            FROM pg_class pg_c
            JOIN pg_namespace pg_n ON pg_n.oid = pg_c.relnamespace
            WHERE pg_n.nspname = current_schema
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
                JOIN information_schema.key_column_usage AS kcu ON tc.constraint_name = kcu.constraint_name
                                                               AND tc.table_schema = kcu.table_schema
                JOIN information_schema.constraint_column_usage AS ccu ON ccu.constraint_name = tc.constraint_name
                                                                      AND ccu.table_schema = tc.table_schema
                JOIN big_tables bt1 ON bt1.relation_name = tc.table_name
            WHERE constraint_type = 'FOREIGN KEY' AND kcu.column_name NOT IN ('write_uid','create_uid')
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
        [util.BIG_TABLE_THRESHOLD],
    )

    for index_name, table_name, column_name in cr.fetchall():
        util.ENVIRON["__created_fk_idx"].append(index_name)
        create_index_queries.append("CREATE INDEX %s ON %s(%s)" % (index_name, table_name, column_name))

    if create_index_queries:
        _logger.info("creating %s indexes (might be slow)", len(create_index_queries))
        util.parallel_execute(cr, create_index_queries)


class Model(models.Model):
    _inherit = "ir.model"
    _module = "base"

    @api.model
    def _register_hook(self):
        super(Model, self)._register_hook()
        index_names = util.ENVIRON.get("__created_fk_idx", [])
        if index_names:
            drop_index_queries = []
            for index_name in index_names:
                drop_index_queries.append('DROP INDEX IF EXISTS "%s"' % (index_name,))
            _logger.info("dropping %s indexes", len(drop_index_queries))
            util.parallel_execute(self.env.cr, drop_index_queries)
