# -*- coding: utf-8 -*-
from odoo.addons.sale_stock_renting import _ensure_rental_stock_moves_consistency

from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # Force the post_init_hook configuration
    if util.version_gte("saas~16.2"):
        env = util.env(cr)
        _ensure_rental_stock_moves_consistency(env)

    else:
        _ensure_rental_stock_moves_consistency(cr, False)
