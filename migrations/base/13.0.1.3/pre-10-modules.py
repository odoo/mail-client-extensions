# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.new_module(cr, "l10n_il", deps={"account"})
    util.new_module(cr, "l10n_lt", deps={"l10n_multilang"})
    util.new_module(cr, "l10n_dk", deps={"account", "base_iban", "base_vat"})
    if util.has_enterprise():
        util.module_deps_diff(cr, "crm_enterprise", plus={"web_map"})
        util.merge_module(cr, "l10n_mx_edi_payment", "l10n_mx_edi")
        util.merge_module(cr, "account_reports_cash_flow", "account_reports")
