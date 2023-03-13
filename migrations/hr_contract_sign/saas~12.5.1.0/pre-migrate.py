# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.move_field_to_module(cr, "hr.contract", "sign_request_ids", "hr_contract_salary", "hr_contract_sign")
    util.move_field_to_module(cr, "hr.contract", "sign_request_count", "hr_contract_salary", "hr_contract_sign")

    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("hr_contract_{salary,sign}.sign_item_role_job_responsible"))
