# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_view(cr, 'account.view_account_report_tree_hierarchy')
    util.remove_record(cr, 'account.menu_account_report_tree_hierarchy')
    util.remove_record(cr, 'account.action_account_report_tree_hierarchy')
