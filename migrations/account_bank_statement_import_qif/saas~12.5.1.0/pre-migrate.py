# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_view(cr, "account_bank_statement_import_qif.account_bank_statement_import_view_inherited")
