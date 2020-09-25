# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "l10n_be_coda.view_bank_statement_line_coda_form")
    util.remove_view(cr, "l10n_be_coda.view_account_bank_statement_line_coda_tree")
    util.remove_view(cr, "l10n_be_coda.view_bank_statement_line_coda_filter")
    util.remove_record(cr, "l10n_be_coda.action_account_bank_statement_line_coda")
