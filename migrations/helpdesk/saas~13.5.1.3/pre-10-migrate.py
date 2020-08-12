# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_m2m(cr, "helpdesk_sla_helpdesk_stage_rel", "helpdesk_sla", "helpdesk_stage")

    cr.execute(
        """
        INSERT INTO helpdesk_sla_helpdesk_stage_rel
               (helpdesk_sla_id, helpdesk_stage_id)
        SELECT s.id, s.exclude_stage_id
        FROM helpdesk_sla s
        WHERE s.exclude_stage_id IS NOT NULL"""
    )

    util.remove_field(cr, "helpdesk.sla", "exclude_stage_id")

    util.remove_view(cr, 'helpdesk.helpdesk_ticket_view_kanban_no_create')

    util.remove_record(cr, 'helpdesk.helpdesk_ticket_action_main')
    util.remove_record(cr, 'helpdesk.action_upcoming_sla_fail_tickets')
    util.remove_record(cr, 'helpdesk.helpdesk_ticket_action_high_priorities')
    util.remove_record(cr, 'helpdesk.helpdesk_ticket_action_urgent')
    util.remove_record(cr, 'helpdesk.helpdesk_ticket_action_sla_high')
    util.remove_record(cr, 'helpdesk.helpdesk_ticket_action_sla_urgent')
    util.remove_record(cr, 'helpdesk.helpdesk_ticket_action_Archived')
    util.remove_record(cr, 'helpdesk.helpdesk_ticket_action_slafailed')
    util.remove_record(cr, 'helpdesk.helpdesk_ticket_action_dashboard_high_priority')
    util.remove_record(cr, 'helpdesk.helpdesk_ticket_action_dashboard_urgent')
