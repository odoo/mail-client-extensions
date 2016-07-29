# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.rename_model(
        cr,
        'report.account_extra_reports.report_journal',
        'report.account.report_journal',
        rename_table=False)
    util.rename_model(
        cr,
        'report.account_extra_reports.report_partnerledger',
        'report.account.report_partnerledger',
        rename_table=False)
