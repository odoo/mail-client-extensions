# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "account.view_move_line_tree_grouped")
    util.remove_view(cr, "account.view_account_move_line_filter_with_root_selection")
    util.remove_record(cr, "account.action_account_moves_ledger_general")
