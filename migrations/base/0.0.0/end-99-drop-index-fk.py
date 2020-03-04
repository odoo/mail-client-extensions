# -*- coding: utf-8 -*-
import logging
from odoo.addons.base.maintenance.migrations import util

NS = "odoo.addons.base.maintenance.migrations.base."
_logger = logging.getLogger(NS + __name__)


def migrate(cr, version):
    index_names = util.ENVIRON.get("__created_fk_idx", [])
    if index_names:
        drop_index_queries = []
        for index_name in index_names:
            drop_index_queries.append('DROP INDEX IF EXISTS "%s"' % (index_name,))
        _logger.info("dropping %s indexes", len(drop_index_queries))
        util.parallel_execute(cr, drop_index_queries)
