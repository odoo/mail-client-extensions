# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_field(cr, "hr.applicant", "default_contract_id")
    util.remove_field(cr, "hr.job", "signature_request_template_id")
    util.remove_field(cr, "hr.job", "contract_update_template_id")
    util.create_column(cr, "hr_contract", "contract_type", "varchar")

    util.remove_view(cr, "hr_contract_salary.hr_employee_view_form")
