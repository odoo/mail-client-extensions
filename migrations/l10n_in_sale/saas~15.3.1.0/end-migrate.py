# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    if util.module_installed(cr, "sale_subscription"):
        cr.execute(
            """
            SELECT id
              FROM sale_order
             WHERE l10n_in_gst_treatment IS NULL
               AND is_subscription = True
            """
        )
        sale_ids = [id[0] for id in cr.fetchall()]
        util.recompute_fields(cr, "sale.order", ["l10n_in_gst_treatment"], ids=sale_ids)
