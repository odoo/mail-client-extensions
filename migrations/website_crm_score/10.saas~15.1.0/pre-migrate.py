# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'website_crm_score', 'last_run', 'timestamp without time zone')
    cr.execute("""
      WITH last_leads AS (
        SELECT create_date, score_id
          FROM crm_lead l
          JOIN (
                SELECT max(lead_id) as lead_id, score_id
                  FROM crm_lead_score_rel
              GROUP BY score_id) r ON (r.lead_id = l.id)
      )
      UPDATE website_crm_score s
         SET last_run = l.create_date
        FROM last_leads l
       WHERE s.id = l.score_id
    """)
