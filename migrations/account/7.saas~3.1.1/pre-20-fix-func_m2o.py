# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util
def migrate(cr, version):
    # m2o function fields now have foreign keys...
    util.ensure_m2o_func_field_data(cr, 'account_move', 'partner_id', 'res_partner')
    util.ensure_m2o_func_field_data(cr, 'account_invoice_line', 'partner_id', 'res_partner')
    util.ensure_m2o_func_field_data(cr, 'account_invoice', 'commercial_partner_id', 'res_partner')
