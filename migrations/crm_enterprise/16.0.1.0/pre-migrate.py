# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    # removed record
    util.remove_record(cr, "crm_enterprise.action_report_crm_lead_salesteam_view_dashboard")
    util.remove_record(cr, "crm_enterprise.crm_opportunity_action_dashboard_dashboard")
    util.remove_record(cr, "crm_enterprise.crm_lead_action_dashboard")
    util.remove_record(cr, "crm_enterprise.crm_lead_action_dashboard_dashboard")
    util.remove_record(cr, "crm_enterprise.crm_lead_action_dashboard_pivot")
    util.remove_record(cr, "crm_enterprise.crm_lead_action_dashboard_graph")
    util.remove_record(cr, "crm_enterprise.crm_lead_action_partner_view_dashboard")
    util.remove_record(cr, "crm_enterprise.crm_opportunity_report_action_lead_dashbaord")
    util.remove_record(cr, "crm_enterprise.crm_enterprise_dashboard_menu")

    # removed view
    util.remove_view(cr, "crm_enterprise.crm_opportunity_view_dashboard")
    util.remove_view(cr, "crm_enterprise.crm_lead_dashboard_view")
