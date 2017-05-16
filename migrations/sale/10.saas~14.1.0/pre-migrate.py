# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute("UPDATE crm_team SET use_invoices=true")

    team = util.ref(cr, 'sales_team.salesteam_website_sales')
    if team:
        cr.execute("UPDATE crm_team SET use_invoices=false WHERE id=%s",
                   [team])
