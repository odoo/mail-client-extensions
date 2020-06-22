# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_view(cr, "stock.view_pack_operation_lot_form")
