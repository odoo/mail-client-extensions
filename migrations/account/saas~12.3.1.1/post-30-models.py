# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_field(cr, "account.account", "last_time_entries_checked")
    util.remove_field(cr, "account.tax", "account_id")
    util.remove_field(cr, "account.tax", "refund_account_id")
    util.remove_field(cr, "account.move", "auto_reverse")
    util.remove_field(cr, "account.move", "reverse_date")
