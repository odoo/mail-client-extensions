# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    for data in [
        "l10n_be_hospital_insurance",
        "l10n_be_hospital_insurance_value_0",
        "l10n_be_hospital_insurance_value_1",
        "l10n_be_insured_spouse",
        "l10n_be_insured_children",
        "l10n_be_insured_adults",
    ]:
        util.rename_xmlid(cr, f"hr_contract_salary_internal.{data}", f"l10n_be_hr_contract_salary.{data}")
