# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.env(cr)['account.journal']._enable_batch_deposit_on_bank_journals()
