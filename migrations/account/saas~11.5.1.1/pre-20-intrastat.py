# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.module_installed(cr, "l10n_be_intrastat"):
        util.move_field_to_module(cr, "account.invoice", "incoterm_id", "l10n_be_intrastat", "account")
        util.move_field_to_module(cr, "res.company", "incoterm_id", "l10n_be_intrastat", "account")
    else:
        util.create_column(cr, "res_company", "incoterm_id", "int4")
        util.create_column(cr, "account_invoice", "incoterm_id", "int4")
