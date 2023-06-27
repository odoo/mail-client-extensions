# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    records_to_update_xmlid = [
        "l10n_be_monthly_net",
        "l10n_be_monthly_cash",
        "l10n_be_non_financial_benefits",
        "l10n_be_yearly_cash",
        "hr_contract_benefit_action",
    ]
    for record in records_to_update_xmlid:
        util.if_unchanged(cr, f"hr_contract_salary.{record}", util.update_record_from_xml)
