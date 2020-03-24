# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):

    util.move_field_to_module(cr, "hr.contract", "structure_type_id", "hr_payroll", "hr_contract")
    util.remove_field(cr, 'hr.contract', 'advantages')
