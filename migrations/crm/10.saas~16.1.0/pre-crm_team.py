# -*- coding: utf-8 -*-

def migrate(cr, version):
    cr.execute("""
        UPDATE crm_team
           SET dashboard_graph_model = 'crm.opportunity.report'
         WHERE dashboard_graph_model = 'pipeline'
    """)
