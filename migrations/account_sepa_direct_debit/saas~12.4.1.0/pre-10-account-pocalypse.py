# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.force_noupdate(cr, 'account_sepa_direct_debit.sdd_mt_invoice_paid_with_mandate', noupdate=False)

    util.create_column(cr, 'account_move', 'sdd_paying_mandate_id', 'int4')
