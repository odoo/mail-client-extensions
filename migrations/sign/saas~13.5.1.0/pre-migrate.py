# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("{hr_contract_,}sign.group_sign_employee"))
    util.remove_record(cr, "sign.access_sign_request_group_user")
    util.remove_record(cr, "sign.ir_rule_sign_template_group_sign_user_employees")
