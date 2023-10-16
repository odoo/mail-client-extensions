# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "account.journal", "alias_auto_extract_pdfs_only")
    util.remove_field(cr, "account.journal", "display_alias_auto_extract_pdfs_only")
    util.remove_view(cr, "account_invoice_extract.view_account_journal_form")
