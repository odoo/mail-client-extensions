# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, 'account_move', 'intrastat_transport_mode_id', 'int4')
    util.create_column(cr, 'account_move', 'intrastat_country_id', 'int4')

    util.create_column(cr, 'account_move_line', 'intrastat_transaction_id', 'int4')
