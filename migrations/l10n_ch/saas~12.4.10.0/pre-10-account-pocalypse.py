# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, 'account_move', 'l10n_ch_isr_number', 'varchar')
