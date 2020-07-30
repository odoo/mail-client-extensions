# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, 'account_move', 'l10n_it_send_state', 'varchar')
    util.create_column(cr, 'account_move', 'l10n_it_stamp_duty', 'float8')
    util.create_column(cr, 'account_move', 'l10n_it_ddt_id', 'int4')
    util.create_column(cr, 'account_move', 'l10n_it_einvoice_name', 'varchar')
    util.create_column(cr, 'account_move', 'l10n_it_einvoice_id', 'int4')
