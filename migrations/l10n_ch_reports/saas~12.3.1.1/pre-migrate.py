# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    ch_id = util.ref(cr, "l10n_ch_reports.financial_report_l10n_ch")
    if ch_id:
       util.remove_menus(cr, [util.ref(cr, "l10n_ch_reports.account_financial_html_report_menu_{0}".format(ch_id))])

    util.remove_record(cr, "l10n_ch_reports.financial_report_l10n_ch")
