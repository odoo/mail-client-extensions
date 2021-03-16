# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.force_noupdate(cr, 'documents_account.vendor_bill_rule', noupdate=False)
    util.force_noupdate(cr, 'documents_account.credit_note_rule', noupdate=False)
    util.force_noupdate(cr, 'documents_account.customer_invoice_rule', noupdate=False)
    util.force_noupdate(cr, 'documents_account.credit_note_rule', noupdate=False)

    util.create_column(cr, 'account_move', 'document_request_line_id', 'int4')
    cr.execute(
        """
        UPDATE documents_workflow_rule
           SET create_model = replace(create_model, '.invoice', '.move')
         WHERE create_model IN ('account.invoice.in_invoice',
                                'account.invoice.out_invoice',
                                'account.invoice.in_refund',
                                'account.invoice.out_refund')
        """
    )
