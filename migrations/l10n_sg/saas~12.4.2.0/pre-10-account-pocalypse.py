# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, 'account_move', 'l10n_sg_permit_number', 'varchar')
    util.create_column(cr, 'account_move', 'l10n_sg_permit_number_date', 'date')
