# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "stock_picking_batch", "company_id", "int4")
    cr.execute(
        """
        UPDATE stock_picking_batch b
           SET company_id = p.company_id
          FROM stock_picking p
         WHERE p.batch_id = b.id
    """
    )
