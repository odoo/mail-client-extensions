# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_view(cr, 'crm.view_partners_form_crm_calls')

    # keep NULL as default value, no need to set them to 0
    util.create_column(cr, 'res_users', 'target_sales_done', 'int4')
    util.create_column(cr, 'res_users', 'target_sales_won', 'int4')
