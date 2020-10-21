# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    if util.ENVIRON.get("procurement_jit_uninstalled"):
        # not installed means it was manually deactivated => they want manual under new scheme
        cr.execute(
            """
            UPDATE stock_picking_type
               SET reservation_method = 'manual'
             WHERE code = 'outgoing'
        """
        )
