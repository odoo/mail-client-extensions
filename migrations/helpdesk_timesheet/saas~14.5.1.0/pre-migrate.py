# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "helpdesk_timesheet.helpdesk_timer_ticket_view_kanban")
