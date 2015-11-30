# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    for view in "view_account_move_line_form_inherit view_invoice_revenue_recognition_category view_account_asset_asset_tree".split():
        util.remove_view(cr, "account_asset." + view)
