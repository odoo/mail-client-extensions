# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    eb = util.expand_braces

    util.rename_xmlid(cr, "crm.action_crm_tag_kanban_view_oppor11", "crm.crm_lead_opportunities_view_kanban")
    util.rename_xmlid(cr, "crm.action_crm_tag_tree_view_oppor11", "crm.crm_lead_opportunities_view_tree")
    util.rename_xmlid(cr, "crm.action_crm_tag_form_view_oppor11", "crm.crm_lead_opportunities_view_form")
    util.rename_xmlid(cr, *eb("crm.crm_menu_{pipeline,sales}"))

    util.remove_record(cr, "crm.email_template_opportunity_reminder_mail")
    util.remove_record(cr, "crm.mail_template_data_module_install_crm")

    cr.execute(
        "DELETE FROM ir_act_window_view WHERE act_window_id IN %s",
        [(util.ref(cr, "crm.crm_lead_opportunities_tree_view"), util.ref(cr, "crm.crm_lead_all_leads"))],
    )
