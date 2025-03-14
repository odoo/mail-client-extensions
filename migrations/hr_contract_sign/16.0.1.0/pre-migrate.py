from odoo.upgrade import util


def migrate(cr, version):
    records = [
        "hr_contract_sign.ir_rule_sign_request_item_group_sign_user",
        "hr_contract_sign.access_sign_request_group_employee",
        "hr_contract_sign.access_sign_request_item_group_employee",
    ]
    for record in records:
        util.remove_record(cr, record)
