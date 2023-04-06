# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "l10n_in_hr_payroll.report_india_payslip")
    util.remove_view(cr, "l10n_in_hr_payroll.view_res_company_da")

    util.delete_unused(cr, "l10n_in_hr_payroll.structure_0002")

    util.rename_field(cr, "res.company", "dearness_allowance", "l10n_in_dearness_allowance")

    for field in ["uan", "pan", "esic_number"]:
        util.rename_field(cr, "hr.employee", field, f"l10n_in_{field}")

    for field in [
        "tds",
        "driver_salay",
        "medical_insurance",
        "voluntary_provident_fund",
        "house_rent_allowance_metro_nonmetro",
        "supplementary_allowance",
    ]:
        util.rename_field(cr, "hr.contract", field, f"l10n_in_{field}")
