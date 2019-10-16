# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_column(cr, "fleet_vehicle", "co2_fee")
    util.remove_column(cr, "fleet_vehicle", "total_depreciated_cost")

    util.create_column(cr, 'hr_payslip', 'vehicle_id', 'int4')
