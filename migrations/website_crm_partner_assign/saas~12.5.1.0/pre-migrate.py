# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("website_crm_partner_assign.view_crm{,_lead}_opportunity_geo_assign_form"))
    util.remove_view(cr, "website_crm_partner_assign.view_crm_lead_geo_assign_form")
    util.remove_record(cr, "website_crm_partner_assign.action_assign_salesman_according_assigned_partner")
