# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.env(cr)["res.config.settings"].create({"group_products_in_bills": True}).execute()
