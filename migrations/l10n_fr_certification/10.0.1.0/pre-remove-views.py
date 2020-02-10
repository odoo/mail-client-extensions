# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_view(cr, 'l10n_fr_certification.bank_statement_draft_form_inherit')
    util.remove_view(cr, 'l10n_fr_certification.invoice_form_no_cancel_inherit')
    util.remove_view(cr, 'l10n_fr_certification.view_move_form_no_cancel_inherit')
