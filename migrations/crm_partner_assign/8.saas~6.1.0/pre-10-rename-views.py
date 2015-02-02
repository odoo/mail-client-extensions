# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.rename_xmlid(cr, 'crm_partner_assign.view_report_crm_lead_assign_graph',
                          'crm_partner_assign.view_report_crm_lead_assign_pivot')
