from odoo.upgrade import util


def migrate(cr, version):
    util.update_record_from_xml(cr, "hr_contract.group_hr_contract_employee_manager", from_module="hr_contract")
    util.update_record_from_xml(cr, "hr_contract.group_hr_contract_manager", from_module="hr_contract")
