# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.remove_view(cr, "helpdesk.helpdesk_ticket_action_close_analysis_graph_inherit_dashboard")
    util.rename_xmlid(cr, *eb("helpdesk.helpdesk_ticket_action_7days{,_}success_tree"))
    util.rename_xmlid(cr, *eb("helpdesk.helpdesk_ticket_action_7days{,_}success_kanban"))
    util.rename_xmlid(cr, *eb("helpdesk.helpdesk_ticket_action_7days{,_}success_activity"))
    util.rename_xmlid(cr, *eb("helpdesk.helpdesk_ticket_action_7days{,_}success_pivot"))
    util.rename_xmlid(cr, *eb("helpdesk.helpdesk_ticket_action_7days{,_}success_graph"))
    util.remove_record(cr, "helpdesk.helpdesk_ticket_action_7dayssuccess_cohort")
    util.remove_record(cr, "helpdesk.model_helpdesk_ticket_action_share")
