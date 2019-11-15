# -*- coding: utf-8 -*-
import logging
from odoo.addons.base.maintenance.migrations import util

_logger = logging.getLogger("odoo.addons.base.maintenance.migrations.base." + __name__)


def migrate(cr, version):
    if not util.column_exists(cr, "ir_model_data", "studio"):
        return

    cr.execute(
        """
            UPDATE ir_model_data
               SET noupdate = false
             WHERE model = 'ir.ui.view'
               AND noupdate = true
               AND studio = true
               AND module != 'studio_customization'
         RETURNING module, name
        """
    )

    for module, name in cr.fetchall():
        _logger.info("force update of builtin view %s.%s", module, name)
