import logging

from odoo.upgrade import util

_logger = logging.getLogger("odoo.upgrade.analytic.17.0." + __name__)


def migrate(cr, version):
    drop_index_queries = []
    update_dist_queries = []

    for inh in util.for_each_inherit(cr, "analytic.mixin"):
        table = util.table_of_model(cr, inh.model)
        if util.column_exists(cr, table, "analytic_distribution"):
            update_dist_queries.append(
                util.format_query(
                    cr,
                    "UPDATE {} SET analytic_distribution = NULL WHERE jsonb_typeof(analytic_distribution) != 'object'",
                    table,
                )
            )
            drop_index_queries.append(
                util.format_query(cr, "DROP INDEX IF EXISTS {}", f"{table}_analytic_distribution_gin_index")
            )

    util.parallel_execute(cr, update_dist_queries)

    _logger.info("dropping %s indexes", len(drop_index_queries))
    util.parallel_execute(cr, drop_index_queries)
