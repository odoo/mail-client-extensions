from odoo.upgrade import util


def migrate(cr, version):
    util.move_field_to_module(cr, "hr.contract", "default_contract_id", "hr_contract_salary", "hr_contract")
