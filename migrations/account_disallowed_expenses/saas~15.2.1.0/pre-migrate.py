# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "account_disallowed_expenses.view_account_disallowed_expenses_rate_form")
