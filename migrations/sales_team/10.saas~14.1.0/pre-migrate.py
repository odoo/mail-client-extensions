# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'crm_team', 'team_type', 'varchar')
    cr.execute("UPDATE crm_team SET team_type='sales', use_invoices=true")

    team = util.ref(cr, 'sales_team.salesteam_website_sales')
    if team:
        cr.execute("UPDATE crm_team SET team_type='website', use_invoices=false WHERE id=%s",
                   [team])
