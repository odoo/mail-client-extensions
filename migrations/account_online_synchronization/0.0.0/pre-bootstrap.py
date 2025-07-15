# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # create empty column for new install
    util.create_column(cr, "account_bank_statement_line", "online_link_id", "int4")
