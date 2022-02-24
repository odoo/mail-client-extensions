# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_m2m(
        cr, "hr_contract_sign_document_wizard_hr_employee_rel", "hr_employee", "hr_contract_sign_document_wizard"
    )
    util.remove_field(cr, "hr.contract.sign.document.wizard", "employee_id")
