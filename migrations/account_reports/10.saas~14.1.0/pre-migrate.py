# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):

    # remove context models
    models = util.splitlines("""
        # context models
        account.report.context.common
        account.context.aged.receivable
        account.context.aged.payable
        account.report.context.bank.rec
        account.financial.html.report.context
        account.report.context.followup.all
        account.report.context.followup
        account.context.general.ledger
        account.report.context.tax
        account.partner.ledger.context
        account.context.coa

        # l10n_be context models
        l10n.be.partner.vat.intra.context
        l10n.be.partner.vat.listing.context

        # manager models
        account.report.footnote
        account.report.footnotes.manager
        account.report.multicompany.manager
        account.report.analytic.manager
        account.report.tag.ilike

        account.report.type
    """)
    for model in models:
        util.delete_model(cr, model)

    util.remove_field(cr, 'account.financial.html.report', 'report_type')
    cr.execute("UPDATE ir_model_data SET noupdate=false WHERE model='account.financial.html.report'")

    cr.execute("UPDATE ir_act_client SET tag='account_report' WHERE tag='account_report_generic'")

    views = util.splitlines("""
        report_financial        # will drop a lot of other templates in cascade...
        report_financial_body
    """)
    for v in views:
        util.remove_view(cr, 'account_reports.' + v)
