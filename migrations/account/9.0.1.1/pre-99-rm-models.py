# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):

    """
        Delete all models that are not used anymore
    """
    util.delete_model(cr, 'account.fiscalyear')
    # util.delete_model(cr, 'account.period')
    util.delete_model(cr, 'account.journal.period')
    # util.delete_model(cr, 'account.move.reconcile')
    util.delete_model(cr, 'account.installer')
    util.delete_model(cr, 'account.automatic.reconcile')
    util.delete_model(cr, 'account.move.line.reconcile.select')
    util.delete_model(cr, 'account.move.line.unreconcile.select')
    util.delete_model(cr, 'account.unreconcile.reconcile')
    util.delete_model(cr, 'account.period.close')
    util.delete_model(cr, 'account.fiscalyear.close')
    util.delete_model(cr, 'account.fiscalyear.close.state')
    util.delete_model(cr, 'account.open.closed.fiscalyear')
    util.delete_model(cr, 'report.account.report_centraljournal')
    util.delete_model(cr, 'report.account.report_generaljournal')
    util.delete_model(cr, 'report.account.report_journal')
    util.delete_model(cr, 'report.account.report_salepurchasejournal')
    util.delete_model(cr, 'report.account.report_partnerbalance')
    util.delete_model(cr, 'report.account.report_partnerledger')
    util.delete_model(cr, 'report.account.report_partnerledgerother')
    util.delete_model(cr, 'report.account.report_vat')
    util.delete_model(cr, 'report.account.receivable')
    util.delete_model(cr, 'report.aged.receivable')
    util.delete_model(cr, 'report.invoice.created')
    util.delete_model(cr, 'report.account_type.sales')
    util.delete_model(cr, 'report.account.sales')
    util.delete_model(cr, 'account.treasury.report')
    util.delete_model(cr, 'analytic.entries.report')
    util.delete_model(cr, 'account.entries.report')
    util.delete_model(cr, 'temp.range')
    # Wizard
    util.delete_model(cr, 'account.statement.from.invoice.lines')
    util.delete_model(cr, 'account.change.currency')
    util.delete_model(cr, 'account.general.journal')
    util.delete_model(cr, 'account.central.journal')
    util.delete_model(cr, 'account.print.journal')
    util.delete_model(cr, 'account.state.open')
    util.delete_model(cr, 'account.use.model')
    util.delete_model(cr, 'validate.account.move.lines')
    util.delete_model(cr, 'account.tax.chart')
    util.delete_model(cr, 'account.chart')
    util.delete_model(cr, 'account.vat.declaration')
    util.delete_model(cr, 'account.partner.balance')
    util.delete_model(cr, 'account.partner.ledger')
    util.delete_model(cr, 'account.subscription.generate')
    util.delete_model(cr, 'account.move.bank.reconcile')
    util.delete_model(cr, 'account.journal.select')
    util.delete_model(cr, 'account.partner.reconcile.process')
    util.delete_model(cr, 'account.common.journal.report')
    util.delete_model(cr, 'account.addtmpl.wizard')

    # To check
    # account.statement.operation.template
    # account.journal.cashbox.line
    # account.tax.code.template
    # account.subscription.line
    # account.subscription
    # account.model.line
    # account.model
    # account.tax.code
    # account.analytic.journal (in analytic)

