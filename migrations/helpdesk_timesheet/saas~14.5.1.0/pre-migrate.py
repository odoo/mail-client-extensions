# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "helpdesk_timesheet.helpdesk_timer_ticket_view_kanban")
    util.remove_view(cr, "helpdesk_timesheet.project_project_view_project_tickets_kanban_inherited")
    util.remove_view(cr, "helpdesk_timesheet.view_helpdesk_ticket_graph_analysis")
    util.remove_view(cr, "helpdesk_timesheet.view_helpdesk_ticket_pivot_analysis")
