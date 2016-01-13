# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_view(cr, 'crm.view_partners_form_crm_calls')

    # keep NULL as default value, no need to set them to 0
    util.create_column(cr, 'res_users', 'target_sales_done', 'int4')
    util.create_column(cr, 'res_users', 'target_sales_won', 'int4')

    # link default stages
    cr.execute("""
        INSERT INTO crm_team_stage_rel(stage_id, team_id)
        SELECT s.id, t.id
          FROM crm_stage s, crm_team t
         WHERE s.case_default = true
           AND NOT EXISTS(SELECT 1 FROM crm_team_stage_rel WHERE stage_id=s.id AND team_id=t.id)
    """)

    # deactivate lost/dead leads
    # same heuristic as case_makr_lost method in 8.0 (and saas-6): https://git.io/vzZo8
    cr.execute("""
        UPDATE crm_lead l
          FROM active = false, probability = 0
         USING crm_stage s
         WHERE s.id = l.stage_id
           AND s.probability = 0
           AND s.on_change = true
           AND s.sequence > 1
    """)

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
