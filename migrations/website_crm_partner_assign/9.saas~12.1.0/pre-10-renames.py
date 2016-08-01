# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.rename_xmlid(cr,
                      'website_crm_partner_assign.access_ crm_lead_report_assign',
                      'website_crm_partner_assign.access_crm_lead_report_assign')
    util.rename_xmlid(cr,
                      'website_crm_partner_assign.access_ crm_lead_report_assign_all',
                      'website_crm_partner_assign.access_crm_lead_report_assign_all')

    util.delete_model(cr, 'crm.lead.channel.interested')        # rename to /dev/null (hum...)
