# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_model(cr, "account.bank.statement.import.journal.creation")
    util.remove_model(cr, "account.bank.statement.import")
