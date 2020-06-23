# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "account.financial.html.report", "hierarchy_option")

    util.remove_record(cr, "account_reports.action_journal_items")
    util.remove_view(cr, "account_reports.search_template_extra_options_generic_tax_report")
