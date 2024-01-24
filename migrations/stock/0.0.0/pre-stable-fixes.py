# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.version_between("14.0", "17.0"):
        # non-stored field remove in stable version.
        # See https://github.com/odoo/odoo/pull/120048
        util.remove_field(cr, "report.stock.quantity", "move_ids")

    if util.version_between("16.0", "17.0"):
        env = util.env(cr)
        user_group = env.ref("base.group_user")
        portal_group = env.ref("base.group_portal")
        stock_group = env.ref("stock.group_production_lot")
        if stock_group in user_group.implied_ids:
            portal_group._apply_group(stock_group)
