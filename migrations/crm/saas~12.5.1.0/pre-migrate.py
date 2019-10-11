# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # TODO adapt saas-12.4 script to not set {phone,email}_state to `empty`
    # cr.execute("UPDATE crm_lead SET phone_state = NULL WHERE phone_state = 'empty'")
    # cr.execute("UPDATE crm_lead SET email_state = NULL WHERE email_state = 'empty'")

    util.create_column(cr, "crm_lead", "lang_id", "int4")
    util.remove_field(cr, "crm.stage", "legend_priority")

    util.create_column(cr, "crm_team", "use_leads", "boolean")
    cr.execute("UPDATE crm_team SET use_leads = true")

    util.create_column(cr, "res_config_settings", "module_crm_iap_lead_enrich", "boolean")
    util.create_column(cr, "res_config_settings", "lead_enrich_auto", "varchar")
    util.remove_field(cr, "res_config_settings", "crm_phone_valid_method")

    # data changes
    eb = util.expand_braces

    util.remove_record(cr, "crm.crm_opportunity_report_action_graph")
    util.remove_view(cr, "crm.crm_case_form_view_leads")
    util.remove_view(cr, "crm.crm_case_form_view_oppor")
    util.remove_view(cr, "crm.view_create_opportunity_simplified")
    util.remove_record(cr, "crm.create_opportunity_simplified")
    util.remove_record(cr, "crm.crm_lead_opportunities_view_form")

    util.rename_xmlid(cr, *eb("crm.crm_lead_{opportunities_tree_view,action_pipeline}"))
    for view in {"kanban", "tree", "calendar", "pivot", "graph"}:
        util.rename_xmlid(cr, *eb("crm.crm_lead_{opportunities_tree_view,action_pipeline}_view_" + view))
    util.remove_record(cr, "crm.crm_lead_opportunities_tree_view_view_form")

    util.remove_record(cr, "crm.action_mark_late_activities_done")
    util.remove_record(cr, "crm.action_mark_activities_done")
    util.remove_record(cr, "crm.crm_lead_action_activities")

    util.remove_record(cr, "crm.menu_crm_leads")

    util.remove_record(cr, "crm.action_crm_tag_form_view_salesteams_oppor11")
    util.remove_record(cr, "crm.calendar_event_partner")
    util.remove_record(cr, "crm.relate_partner_opportunities_form")
    util.remove_record(cr, "cmr.merge_opportunity_act")
