# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "account_reports.main_template_with_filter_input_accounts")
    util.remove_view(cr, "account_reports.main_template_with_filter_input_partner")
