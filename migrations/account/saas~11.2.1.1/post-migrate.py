# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    group = util.env(cr).ref("base.group_user")
    if util.ref(cr, "analytic.group_analytic_accounting") in group.implied_ids.ids:
        group.write({"implied_ids": [(4, util.ref(cr, "analytic.group_analytic_tags"))]})
