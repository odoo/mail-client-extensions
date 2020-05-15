# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_field(cr, "l10n_in.account.invoice.report", "invoice_type")
    util.remove_field(cr, "l10n_in.account.invoice.report", "invoice_id")
    util.remove_field(cr, "l10n_in.account.invoice.report", "refund_invoice_id")
