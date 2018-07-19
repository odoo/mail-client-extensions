# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    eb = util.expand_braces

    util.rename_xmlid(cr, *eb("account.action_{invoice_tree2,vendor_bill_template}"))

    util.remove_view(cr, "account.setup_bank_journal_form")
    util.remove_view(cr, "account.setup_posted_move_form")
    util.remove_view(cr, "account.setup_opening_move_line_tree")
