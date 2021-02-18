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
