# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "utm.campaign", "crm_lead_activated", "use_leads")
    util.rename_field(cr, "utm.campaign", "lead_count", "crm_lead_count")
    util.update_field_references(cr, "opportunity_count", "crm_lead_count", only_models=("utm.campaign",))
    util.remove_field(cr, "utm.campaign", "opportunity_count")

    util.remove_view(cr, "crm.crm_activity_report_view_tree")
