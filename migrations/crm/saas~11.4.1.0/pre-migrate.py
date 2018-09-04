# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "crm_lead", "expected_revenue", "numeric")
    cr.execute("""
        UPDATE crm_lead
           SET expected_revenue =
                 round((COALESCE(planned_revenue, 0) * COALESCE(probability, 0) / 100.0)::numeric, 2)
            WHERE round(expected_revenue, 2) !=
                  round((COALESCE(planned_revenue, 0) * COALESCE(probability, 0) / 100.0)::numeric, 2)
                OR expected_revenue IS NULL
    """)

    cr.execute("""
        UPDATE crm_team
           SET dashboard_graph_model='crm.lead'
         WHERE dashboard_graph_model='crm.opportunity.report'
    """)

    # reassign views/filters/actions
    view_ids = [
        util.ref(cr, "crm.crm_opportunity_report_view_%s" % v)
        for v in {"pivot", "pivot_lead", "graph", "graph_lead", "search"}
    ]
    cr.execute("UPDATE ir_ui_view SET model='crm.lead' WHERE id IN %s", [tuple(view_ids)])

    filter_ids = [
        util.ref(cr, "crm.filter_opportunity_%s" % f)
        for f in {"opportunities_cohort", "opportunities_won_per_team", "country", "expected_revenue"}
    ]
    cr.execute("UPDATE ir_filters SET model_id='crm.lead' WHERE id IN %s", [tuple(filter_ids)])

    action_ids = [
        util.ref(cr, "crm.crm_opportunity_report_%s" % x)
        for x in {"action", "action_graph", "action_lead"}
    ] + [
        util.ref(cr, "crm.action_report_crm_%s_salesteam" % x)
        for x in {"opportunity", "lead"}
    ]
    cr.execute("""
        UPDATE ir_act_window
           SET res_model = 'crm.lead', view_id=NULL
         WHERE id IN %s
    """, [tuple(action_ids)])

    util.remove_model(cr, "crm.opportunity.report")

    # cleanup
    util.remove_view(cr, "crm.crm_case_pivot_view_leads")
    util.remove_view(cr, "crm.crm_case_graph_view_leads")
