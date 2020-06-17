# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, 'account_move_line', 'vehicle_id', 'int4')
    cr.execute("""
        UPDATE account_move_line aml
           SET vehicle_id = vehicle.id
          FROM fleet_vehicle vehicle
         WHERE vehicle.analytic_account_id = aml.analytic_account_id
    """)
    util.remove_field(cr, 'fleet.vehicle', 'analytic_account_id', cascade=True)
    util.remove_view(cr, 'account_fleet.fleet_vehicle_view_form_inherit_account')
