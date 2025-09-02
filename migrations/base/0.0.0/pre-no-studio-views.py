# -*- coding: utf-8 -*-
import logging

from odoo.addons.base.maintenance.migrations import util

_logger = logging.getLogger("odoo.addons.base.maintenance.migrations.base." + __name__)


def migrate(cr, version):
    if util.column_exists(cr, "ir_model_data", "studio"):
        cr.execute(
            r"""
                UPDATE ir_model_data
                   SET noupdate = false
                 WHERE model = 'ir.ui.view'
                   AND noupdate = true
                   AND studio = true
                   AND module != 'studio_customization'
                   AND NOT (   module = 'industry_fsm_report'
                           AND name LIKE 'report\_custom\_%'
                           )
             RETURNING module, name
            """
        )

        for module, name in cr.fetchall():
            _logger.info("force update of builtin view %s.%s", module, name)
