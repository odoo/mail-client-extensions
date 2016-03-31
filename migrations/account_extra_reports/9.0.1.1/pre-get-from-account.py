# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.move_model(cr, 'account.common.journal.report', 'account', 'account_extra_reports')
    util.move_model(cr, 'account.report.partner.ledger', 'account', 'account_extra_reports')
    util.move_model(cr, 'account.print.journal', 'account', 'account_extra_reports')

    for report in "report_partnerledger report_journal".split():
        util.rename_xmlid(cr, 'account.' + report, 'account_extra_reports.' + report)
        util.force_noupdate(cr, 'account_extra_reports.' + report, False)
