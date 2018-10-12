# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    for table in {"account_bank_statement_line", "res_partner"}:
        util.create_column(cr, table, "online_partner_vendor_name", "varchar")
        util.create_column(cr, table, "online_partner_bank_account", "varchar")
