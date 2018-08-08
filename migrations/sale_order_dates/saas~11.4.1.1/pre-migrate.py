# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.rename_field(cr, "sale.order", "commitment_date", "expected_date")
    util.remove_column(cr, "sale_order", "commitment_date")
    util.rename_field(cr, "sale.order", "requested_date", "commitment_date")
