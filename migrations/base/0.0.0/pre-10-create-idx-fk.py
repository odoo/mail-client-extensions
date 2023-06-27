# -*- coding: utf-8 -*-
import logging

from odoo import api, models, release

from odoo.addons.base.maintenance.migrations import util

NS = "odoo.addons.base.maintenance.migrations.base."
_logger = logging.getLogger(NS + __name__)


def migrate(cr, version):
    cr.execute("ANALYZE")  # update statistics
    create_index_queries = []
    util.ENVIRON["__created_fk_idx"] = []

    create_index_queries.append(
        "CREATE INDEX upg_attachment_cleanup_speedup_idx ON ir_attachment(res_model, res_field, id)"
    )
    util.ENVIRON["__created_fk_idx"].append("upg_attachment_cleanup_speedup_idx")
    if util.table_exists(cr, "mail_message"):
        create_index_queries.append(
            "create index tmp_mig_mcplastseenmsg_speedup_idx on mail_message(model, author_id, res_id, id desc)"
        )
        util.ENVIRON["__created_fk_idx"].append("tmp_mig_mcplastseenmsg_speedup_idx")

    if release.version_info[:2] == (16, 0) and util.column_exists(cr, "mail_message", "email_layout_xmlid"):
        create_index_queries.append("CREATE INDEX upg_mailmsg_layout_xid ON mail_message(email_layout_xmlid)")
        util.ENVIRON["__created_fk_idx"].append("upg_mailmsg_layout_xid")

    if util.column_exists(cr, "website_visitor", "push_token"):
        create_index_queries.append(
            "create index tmp_mig_websitevisitortoken_speedup_idx on website_visitor(id) WHERE push_token IS NOT NULL"
        )
        util.ENVIRON["__created_fk_idx"].append("tmp_mig_websitevisitortoken_speedup_idx")

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

    # Return all FK columns from BIG tables
    cr.execute(
        """
        SELECT quote_ident(cl1.relname) AS big_table,
               quote_ident(att1.attname) AS big_table_column,
               s.null_frac > 0.9 -- less than 10 percent is not null
          FROM pg_constraint AS con
          JOIN pg_class AS cl1
            ON con.conrelid = cl1.oid
          JOIN pg_namespace AS pg_n
            ON pg_n.oid = cl1.relnamespace
          JOIN pg_class AS cl2
            ON con.confrelid = cl2.oid
          JOIN pg_attribute AS att1
            ON att1.attrelid = cl1.oid
          JOIN pg_attribute AS att2
            ON att2.attrelid = cl2.oid
     LEFT JOIN pg_stats AS s
            ON s.tablename = cl1.relname
           AND s.attname = att1.attname
           AND s.schemaname = current_schema
     LEFT JOIN pg_index x
            ON x.indrelid = cl1.oid
            -- att1 is one of the KEY columns, not just a included one, included columns won't speed up searches
           AND att1.attnum = ANY (x.indkey[1:x.indnkeyatts])
         WHERE cl1.reltuples >= %s -- arbitrary number saying this is a big table
           AND cl1.relkind = 'r' -- only select the tables
           AND att1.attname NOT IN ('create_uid', 'write_uid')
           AND x.indrelid IS NULL -- there is no index with the included column
           AND pg_n.nspname = current_schema
            -- the rest is to ensure this is a FK
           AND array_lower(con.conkey, 1) = 1
           AND con.conkey[1] = att1.attnum
           AND att2.attname = 'id'
           AND array_lower(con.confkey, 1) = 1
           AND con.confkey[1] = att2.attnum
           AND con.contype = 'f'
        """,
        [util.BIG_TABLE_THRESHOLD],
    )
    for i, (big_table, big_table_column, partial) in enumerate(cr.fetchall(), start=1):
        index_name = "upgrade_fk_related_idx_{}".format(i)
        util.ENVIRON["__created_fk_idx"].append(index_name)
        query = "CREATE INDEX {index_name} ON {big_table}({big_table_column})"
        if partial:
            query += " WHERE {big_table_column} IS NOT NULL"
        create_index_queries.append(
            query.format(index_name=index_name, big_table=big_table, big_table_column=big_table_column)
        )

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
