# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.rename_xmlid(cr, "delivery.view_delivery_grid_line_tree", "delivery.view_delivery_price_rule_tree")
    util.rename_xmlid(cr, "delivery.view_delivery_grid_line_form", "delivery.view_delivery_price_rule_form")
