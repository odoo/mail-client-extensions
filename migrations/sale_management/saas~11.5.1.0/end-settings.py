# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.module_installed(cr, "sale_quotation_builder"):
        util.env(cr)["res.config.settings"].create({"group_sale_order_template": True}).execute()
