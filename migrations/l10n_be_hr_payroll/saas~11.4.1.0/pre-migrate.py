# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "hr_contract", "final_yearly_costs", "numeric")
    util.create_column(cr, "hr_contract", "transport_mode_car", "boolean")
    util.create_column(cr, "hr_contract", "transport_mode_public", "boolean")
    util.create_column(cr, "hr_contract", "transport_mode_others", "boolean")
    cr.execute("""
        UPDATE hr_contract
           SET transport_mode_car = (transport_mode = 'company_car'),
               transport_mode_public = (transport_mode = 'public_transport'),
               transport_mode_others = (transport_mode = 'others')
    """)
    util.remove_field(cr, "hr.contract", "transport_mode")
