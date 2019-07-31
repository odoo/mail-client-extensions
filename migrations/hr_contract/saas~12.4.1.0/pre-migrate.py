# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_field(cr, "hr.contract", "reported_to_secretariat")
    util.move_field_to_module(cr, "hr.contract", "hr_responsible_id", "hr_contract_salary", "hr_contract")
