# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view('l10n_latam_invoice_document.report_invoice_document')
    util.remove_field(cr, 'account.journal', 'l10n_latam_country_code')