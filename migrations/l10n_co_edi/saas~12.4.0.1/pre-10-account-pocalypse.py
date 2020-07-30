# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, 'account_move', 'l10n_co_edi_datetime_invoice', 'timestamp without time zone')
    util.create_column(cr, 'account_move', 'l10n_co_edi_type', 'varchar')
    util.create_column(cr, 'account_move', 'l10n_co_edi_transaction', 'varchar')
    util.create_column(cr, 'account_move', 'l10n_co_edi_invoice_name', 'varchar')
    util.create_column(cr, 'account_move', 'l10n_co_edi_invoice_status', 'varchar')
    util.create_column(cr, 'account_move', 'l10n_co_edi_attachment_url', 'varchar')
