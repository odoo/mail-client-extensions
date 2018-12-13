# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    set_def = util.env(cr)["ir.default"].set

    def conv(field):
        cr.execute("SELECT default_value FROM hr_contract_advantage_template WHERE code = %s", [field])
        if cr.rowcount:
            [value] = cr.fetchone()
            set_def("hr.contract", field, value)

    for field in {
        "holidays",
        "commission_on_target",
        "fuel_card",
        "representation_fees",
        "internet",
        "mobile",
        "mobile_plus",
        "meal_voucher_amount",
        "eco_checks",
    }:
        conv(field)
