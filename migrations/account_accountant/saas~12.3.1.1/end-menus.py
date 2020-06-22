# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    menus = util.env(cr)["ir.ui.menu"].search([("parent_id", "=", util.ref(cr, "account.menu_finance"))])
    menus.write({"parent_id": util.ref(cr, "account_accountant.menu_accounting")})
