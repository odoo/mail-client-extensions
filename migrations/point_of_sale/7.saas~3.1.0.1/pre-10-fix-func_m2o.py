# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util
def migrate(cr, version):
    # m2o function fields now have foreign keys...
    util.ensure_m2o_func_field_data(cr, 'pos_session', 'cash_register_id', 'account_bank_statement')
    util.ensure_m2o_func_field_data(cr, 'pos_session', 'cash_journal_id', 'account_journal')
