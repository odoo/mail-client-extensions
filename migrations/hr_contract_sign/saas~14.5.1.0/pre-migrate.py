# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "hr.contract.sign.document.wizard", "sign_template_id")

    util.create_m2m(
        cr,
        "hr_contract_sign_document_wizard_sign_template_rel",
        "hr_contract_sign_document_wizard",
        "sign_template",
    )
