# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "crm_enterprise.crm_lead_action_pipeline_view_dashboard")
    util.remove_record(cr, "crm_enterprise.crm_lead_action_pipeline_view_cohort")
