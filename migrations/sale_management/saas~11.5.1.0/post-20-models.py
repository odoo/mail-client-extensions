# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.module_installed(cr, "sale_quotation_builder"):
        util.remove_field(cr, "sale.order.template.line", "layout_category_id")
