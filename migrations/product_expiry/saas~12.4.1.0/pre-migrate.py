# -*- coding: utf-8 -*-

from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "stock_production_lot", "product_expiry_reminded", "boolean")
    util.remove_view(cr, "product_expiry.view_move_form_expiry_simple")
