# -*- coding: utf-8 -*-

def migrate(cr, version):
    cr.execute("""
        UPDATE crm_team
           SET team_type = 'website'
         WHERE id IN (SELECT salesteam_id FROM website)
    """)
