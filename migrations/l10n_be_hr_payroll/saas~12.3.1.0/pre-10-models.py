# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, 'hr_work_entry_type', 'meal_voucher', 'boolean')
    util.remove_field(cr, 'hr.contract', 'social_security_contributions')
    util.remove_field(cr, 'hr.contract', 'yearly_cost_before_charges')
    util.remove_field(cr, 'hr.contract', 'additional_net_amount')
    util.remove_field(cr, 'hr.contract', 'retained_net_amount')
    util.create_column(cr, 'hr_contract', 'fiscal_voluntarism', 'boolean')
    util.create_column(cr, 'hr_contract', 'fiscal_voluntary_rate', 'float8')
    util.create_column(cr, 'hr_employee', 'start_notice_period', 'date')
    util.create_column(cr, 'hr_employee', 'end_notice_period', 'date')
    util.create_column(cr, 'hr_employee', 'first_contract_in_company', 'date')
