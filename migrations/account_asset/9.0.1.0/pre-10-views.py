# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_view(cr, "account_asset.view_account_move_line_form_inherit")
    util.remove_view(cr, "account_asset.view_invoice_revenue_recognition_category")
