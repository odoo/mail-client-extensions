# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    records = util.splitlines(
        """
        hr_salary_rule_bsa_with_pf
        hr_salary_rule_bsa_without_pf
        hr_salary_rule_dcl_with_pf
        hr_salary_rule_dcl_without_pf
        hr_salary_rule_vpa_with_pf
        hr_salary_rule_vpa_without_pf
        DSL
        BSL
    """
    )
    for record in records:
        util.delete_unused(cr, f"l10n_in_hr_payroll.{record}")
