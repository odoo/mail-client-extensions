# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_view(cr, "account.view_account_bank_journal_form")
    util.remove_view(cr, "account.view_account_bank_journal_tree")
    util.remove_view(cr, "account.account_bank_journal_view_kanban")
