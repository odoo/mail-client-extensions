# -*- coding: utf-8 -*-
import logging
from odoo.addons.base.maintenance.migrations import util

NS = "odoo.addons.base.maintenance.migrations.base.saas~11-5."
_logger = logging.getLogger(NS + __name__)


def migrate(cr, version):
    cr.execute("select count(*) from fetchmail_server where action_id IS NOT NULL")
    if cr.fetchone()[0] > 0:
        _logger.warning("You were using server actions in incoming mail servers. This is not supported anymore.")
    util.remove_field(cr, "fetchmail_server", "action_id")
