# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "account_reports.search_template_journals")

    cr.execute("UPDATE account_account SET non_trade = exclude_from_aged_reports")
    util.remove_field(cr, "account.account", "exclude_from_aged_reports")
