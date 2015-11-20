# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_view(cr, 'crm.view_partners_form_crm_calls')

    # keep NULL as default value, no need to set them to 0
    util.create_column(cr, 'res_users', 'target_sales_done', 'int4')
    util.create_column(cr, 'res_users', 'target_sales_won', 'int4')

    # rename some xmlids
    cr.execute("""
        DELETE FROM ir_model_data
              WHERE model='crm.stage'
                AND module='crm'
                AND name IN ('stage_lead2', 'stage_lead5', 'stage_lead7')
    """)
    util.rename_xmlid(cr, 'crm.stage_lead3', 'crm.stage_lead2')
    util.rename_xmlid(cr, 'crm.stage_lead4', 'crm.stage_lead3')
    util.rename_xmlid(cr, 'crm.stage_lead6', 'crm.stage_lead5')
