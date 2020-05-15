# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_field(cr, "account.bank.statement.import", "data_file")
    util.remove_field(cr, "account.bank.statement.import", "filename")
