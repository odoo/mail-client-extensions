# -*- coding: utf-8 -*-

from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    eb = util.expand_braces
    for contract_type in ["pfi", "cdi", "cdd"]:
        util.rename_xmlid(
            cr, *eb("{l10n_be_hr_contract_salary,l10n_be_hr_payroll}.l10n_be_contract_type_%s" % (contract_type))
        )

    # Purpose: The related xpath has been merged into l10n_be_hr_payroll.hr_contract_view_form
    util.remove_view(cr, "l10n_be_hr_payroll.hr_contract_view_form_inherit")

    util.remove_model(cr, "l10n_be.meal.voucher.report")

    util.create_column(cr, "hr_contract", "has_hospital_insurance", "boolean")
    util.create_column(cr, "hr_contract", "insured_relative_children", "int4")
    util.create_column(cr, "hr_contract", "insured_relative_adults", "int4")
    util.create_column(cr, "hr_contract", "insured_relative_spouse", "boolean")
    util.create_column(cr, "hr_contract", "hospital_insurance_amount_per_adult", "float8", default=20.5)
    util.create_column(cr, "hr_contract", "hospital_insurance_amount_per_child", "float8", default=7.2)

    util.create_column(cr, "res_config_settings", "hospital_insurance_amount_child", "float8")
    util.create_column(cr, "res_config_settings", "hospital_insurance_amount_adult", "float8")
