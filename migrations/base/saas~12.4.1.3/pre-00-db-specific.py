# -*- coding: utf-8 -*-
import logging
from odoo.addons.base.maintenance.migrations import util

NS = "odoo.addons.base.maintenance.migrations.base.saas~12.4"
_logger = logging.getLogger(NS + __name__)


def _db_openerp(cr, version):
    cr.execute(
        """
        DELETE FROM openerp_enterprise_database_app
              WHERE module_id = (SELECT id FROM ir_module_module WHERE name='account_voucher')
    """
    )


def migrate(cr, version):
    util.dispatch_by_dbuuid(cr, version, {"8851207e-1ff9-11e0-a147-001cc0f2115e": _db_openerp})
