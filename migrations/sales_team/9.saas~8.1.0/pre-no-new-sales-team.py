# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # crm (saas~8) migration script will try to match each team with stages.
    # If the team defined in data file is about to be created, it will be created without stages.
    # This extra team may force the crm script to fail for no reason.
    # Only create the team if there are no teams.

    data_team = util.ref(cr, 'sales_team.team_sales_department')
    if data_team:
        return

    cr.execute("SELECT count(*) FROM crm_team")
    if not cr.fetchone()[0]:
        return

    cr.execute("""
        INSERT INTO ir_model_data(module, name, model, res_id, noupdate)
             SELECT 'sales_team', 'team_sales_department', 'crm.team', min(id), true
               FROM crm_team
    """)
