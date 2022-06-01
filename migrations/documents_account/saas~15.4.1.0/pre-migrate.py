# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, 'account_move', 'suspense_statement_line_id', 'int4')
    query = '''
        UPDATE account_move move
        SET suspense_statement_line_id = document_line.statement_line_id
        FROM account_move_line document_line
        WHERE document_line.id = move.document_request_line_id
            AND document_line.statement_line_id IS NOT NULL
    '''
    util.parallel_execute(cr, util.explode_query_range(cr, query, table='account_move', alias='move'))

    util.remove_field(cr, 'account.move', 'document_request_line_id')
    util.remove_field(cr, 'account.move.line', 'reconciliation_invoice_id')
    util.remove_field(cr, 'account.reconcile.model', 'activity_type_id')
    util.remove_view(cr, 'documents_account.view_documents_reconcile_model_form')
