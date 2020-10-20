# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "hr_contract_sign.ir_rule_sign_request_group_sign_employee")
    util.remove_record(cr, "hr_contract_sign.ir_rule_sign_request_item_group_sign_employee")
