# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):

    # ===========================================================
    # account_edi + refactoring l10n_mx_edi (PR: 52407 & 12226)
    # ===========================================================

    util.create_column(cr, 'account_edi_format', 'has_web_service', 'boolean', default=False)
    util.create_column(cr, 'account_move', 'edi_state', 'varchar')
    util.remove_field(cr, 'ir.attachment', 'edi_format_id')
    util.remove_field(cr, 'account.edi.format', 'hide_on_journal')
