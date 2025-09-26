# -*- coding: utf-8 -*-
import logging
import os

try:
    from odoo import api, models, release

    from odoo.addons.base.maintenance.migrations import util
except ImportError:
    from openerp import api, models, release

    from openerp.addons.base.maintenance.migrations import util

NS = "odoo.addons.base.maintenance.migrations.base."
_logger = logging.getLogger(NS + __name__)


IDX_AUTO = 0b01
IDX_ANALYZE = 0b10

_DEFAULT_INDEXING = (
    IDX_AUTO if util.str2bool(os.getenv("IS_FIRST_UPGRADE_STEP"), default=False) else IDX_AUTO | IDX_ANALYZE
)
UPG_AUTO_INDEXING = int(os.getenv("UPG_AUTO_INDEXING", _DEFAULT_INDEXING))


def migrate(cr, version):
    if UPG_AUTO_INDEXING & IDX_ANALYZE:
        cr.commit()
        _logger.info("Analyzing DB...")
        cr.execute("ANALYZE")  # update statistics
        _logger.info("Analyze done.")

    if UPG_AUTO_INDEXING & IDX_AUTO == 0:
        _logger.info("Skip auto-indexing")
        return  # nosemgrep: no-early-return

    create_index_queries = []
    util.ENVIRON["__created_fk_idx"] = []
    if util.version_gte("9.0"):
        create_index_queries.append(
            "CREATE INDEX upg_attachment_cleanup_speedup_idx ON ir_attachment(res_model, res_field, id)"
        )
        util.ENVIRON["__created_fk_idx"].append("upg_attachment_cleanup_speedup_idx")

    if release.version_info[:2] == (16, 0) and util.column_exists(cr, "mail_message", "email_layout_xmlid"):
        create_index_queries.append("CREATE INDEX upg_mailmsg_layout_xid ON mail_message(email_layout_xmlid)")
        util.ENVIRON["__created_fk_idx"].append("upg_mailmsg_layout_xid")

    if util.column_exists(cr, "website_visitor", "push_token"):
        create_index_queries.append(
            "create index tmp_mig_websitevisitortoken_speedup_idx on website_visitor(id) WHERE push_token IS NOT NULL"
        )
        util.ENVIRON["__created_fk_idx"].append("tmp_mig_websitevisitortoken_speedup_idx")

    # create indexes on `ir_model{,_fields}` to speed up models/fields deletion
    _logger.info("Search for foreign keys on ir_model and ir_model_fields.")
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
        create_index_queries.append("CREATE INDEX {} ON {}({})".format(index_name, table_name, column_name))

    # Return all FK columns from BIG tables
    _logger.info("Search for foreign keys in big tables.")
    query = util.format_query(
        cr,
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
           AND att1.attnum = ANY (x.indkey[1:x.{}])
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
        "indnkeyatts" if cr._cnx.server_version >= 110000 else "indnatts",
    )
    cr.execute(query, [util.BIG_TABLE_THRESHOLD])
    for i, (big_table, big_table_column, partial) in enumerate(cr.fetchall(), start=1):
        index_name = "upgrade_fk_related_idx_{}".format(i)
        util.ENVIRON["__created_fk_idx"].append(index_name)
        query = "CREATE INDEX {index_name} ON {big_table}({big_table_column})"
        if partial:
            query += " WHERE {big_table_column} IS NOT NULL"
        create_index_queries.append(
            query.format(
                index_name=index_name,
                big_table=big_table,
                big_table_column=big_table_column,
            )
        )

    # create missing indexes on indirect references
    for i, ir in enumerate(util.indirect_references(cr)):
        if ir.company_dependent_comodel:
            continue
        if not ir.res_model:
            # only handle the indexes on `res_model` columns. Indexes on `res_model_id` (FK)
            # are handled by the previous search on BIG tables.
            continue
        args = (ir.res_model, ir.res_id) if ir.res_id else (ir.res_model,)
        if not util.get_index_on(cr, ir.table, *args):
            index_name = "upgrade_ir_idx_{}".format(i)
            util.ENVIRON["__created_fk_idx"].append(index_name)
            query = "CREATE INDEX {} ON {}({})"
            create_index_queries.append(util.format_query(cr, query, index_name, ir.table, util.ColumnList(args, args)))

    if create_index_queries:
        _logger.info("creating %s indexes (might be slow)", len(create_index_queries))
        util.parallel_execute(cr, create_index_queries)


class Model(models.Model):
    _name = "ir.model"
    _inherit = ["ir.model"]
    _module = "base"

    api_model = api.model if util.version_gte("10.0") else lambda x: x

    @api_model
    def _register_hook(self, cr=None):
        if cr is not None:
            super(Model, self)._register_hook(cr)
        else:
            super(Model, self)._register_hook()
            cr = self.env.cr

        index_names = util.ENVIRON.get("__created_fk_idx", [])
        if index_names:
            # pg_stat_get_numscans -> see \d+ pg_stat_all_indexes and
            # https://www.postgresql.org/docs/current/monitoring-stats.html#MONITORING-STATS-VIEWS-TABLE
            query = """
                SELECT pg_stat_get_numscans(x.indexrelid),
                       concat(c.relname, '(', string_agg(a.attname, ',' order by array_position(x.indkey, a.attnum)), ')')
                  FROM pg_index x
                  JOIN pg_class i
                    ON i.oid = x.indexrelid
                  JOIN pg_class c
                    ON c.oid = x.indrelid
                  JOIN pg_attribute a
                    ON a.attrelid = x.indrelid AND ARRAY[a.attnum] <@ x.indkey::int2[]
                  JOIN pg_namespace n
                    ON n.oid = c.relnamespace
                 WHERE n.nspname = current_schema
                   AND i.relname = ANY(%s)
              GROUP BY x.indexrelid, c.relname
              ORDER BY 1 DESC
            """
            cr.execute(query, [index_names])

            count = cr.rowcount
            index_stats = cr.fetchall()

            zero_scan_pc = "{:.2%}".format(sum(1 for (c, _) in index_stats if c == 0) / count)

            n = max(5, len(str(index_stats[0][0])))
            stats = "{0} Scans | Index\n{0}---------------\n".format(" " * (n - 5)) \
                  + "\n".join(" {0:>{n}} | {1}".format(*s, n=n) for s in index_stats)  # fmt: skip
            _logger.info("Auto Indexing Stats: %s unused indexes.\n%s", zero_scan_pc, stats)

            drop_index_queries = [
                util.format_query(cr, "DROP INDEX IF EXISTS {}", index_name) for index_name in index_names
            ]
            _logger.info("dropping %s indexes", len(drop_index_queries))
            util.parallel_execute(cr, drop_index_queries)
