# -*- coding: utf-8 -*-

from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("l10n_fr_reports.account_financial_report_line_03_0_{4,5}_fr_bilan_passif"))
    util.rename_xmlid(cr, *eb("l10n_fr_reports.account_financial_report_line_03_0_{3,4}_fr_bilan_passif"))
    util.rename_xmlid(cr, *eb("l10n_fr_reports.account_financial_report_line_03_0_{2,3}_fr_bilan_passif"))
    util.rename_xmlid(cr, *eb("l10n_fr_reports.account_financial_report_line_03_0_{5_0,2}_fr_bilan_passif"))
