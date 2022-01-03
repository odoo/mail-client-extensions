# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_column(cr, "event_event", "seats_available")
    util.remove_column(cr, "event_event", "seats_reserved")
    util.remove_column(cr, "event_event", "seats_unconfirmed")
    util.remove_column(cr, "event_event", "seats_used")

    util.remove_column(cr, "event_event_ticket", "seats_available")
    util.remove_column(cr, "event_event_ticket", "seats_reserved")
    util.remove_column(cr, "event_event_ticket", "seats_unconfirmed")
    util.remove_column(cr, "event_event_ticket", "seats_used")

    util.remove_record(cr, "event.event_event_menu_pivot_report")
    util.remove_record(cr, "event.event_event_action_pivot")

    util.remove_view(cr, "event.event_event_view_graph")
    util.remove_view(cr, "event.event_event_view_pivot")
