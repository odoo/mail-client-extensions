# -*- coding: utf-8 -*-

def migrate(cr, version):
    cr.execute("""
        UPDATE crm_team
           SET dashboard_graph_model = 'pipeline'
         WHERE dashboard_graph_model IS NULL
           AND use_opportunities = true
    """)
