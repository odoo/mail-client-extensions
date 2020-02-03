# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    eb = util.expand_braces

    util.remove_record(cr, "crm_enterprise.crm_opportunity_action_dashboard_form")
    util.rename_xmlid(cr, *eb("crm_enterprise.crm_lead_{act_window,action_pipeline}_view_cohort"))
