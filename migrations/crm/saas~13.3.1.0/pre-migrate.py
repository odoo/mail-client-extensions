# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_model(cr, "crm.partner.binding")

    util.create_column(cr, "crm_lead2opportunity_partner", "lead_id", "int4")
    util.create_column(cr, "crm_lead2opportunity_partner", "force_assignment", "boolean")
    util.rename_field(cr, "crm.lead2opportunity.partner", "opportunity_ids", "duplicated_lead_ids")

    util.create_column(cr, "crm_lead2opportunity_partner_mass", "lead_id", "int4")
    util.rename_field(cr, "crm.lead2opportunity.partner.mass", "force_assignation", "force_assignment")
    util.rename_field(cr, "crm.lead2opportunity.partner.mass", "opportunity_ids", "duplicated_lead_ids")

    cr.execute('ALTER TABLE "crm_lead_tag_rel" RENAME TO "crm_tag_rel"')

    util.move_field_to_module(cr, "crm.team", "assigned_leads_count", "website_crm_score", "crm")
    util.rename_field(cr, "crm.team", "assigned_leads_count", "lead_all_assigned_month_count")
    util.rename_field(cr, "crm.team", "unassigned_leads_count", "lead_unassigned_count")
    util.rename_field(cr, "crm.team", "overdue_opportunities_count", "opportunities_overdue_count")
    util.rename_field(cr, "crm.team", "overdue_opportunities_amount", "opportunities_overdue_amount")

    util.rename_field(cr, "crm.lead", "phone_blacklisted", "phone_sanitized_blacklisted")
    util.create_column(cr, 'crm_lead', 'phone_sanitized', "varchar")
