# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    """
    Old module, but new dependencies makes it auto installled
    To avoid minutes of computation, compute it manually in case of a new installation
    """
    if util.create_column(cr, "sale_order", "has_delivery", "boolean"):
        cr.execute("""
            UPDATE sale_order s
               SET has_delivery=TRUE
              FROM sale_order_line sol
             WHERE s.id=sol.order_id
               AND sol.is_delivery=true
        """)
