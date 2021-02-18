# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "helpdesk.ticket", "task_id")
    util.remove_field(cr, "helpdesk.ticket", "_related_task_ids")
    util.remove_field(cr, "helpdesk.ticket", "is_closed")
    util.remove_field(cr, "helpdesk.ticket", "is_task_active")
    util.create_column(cr, "helpdesk_ticket", "total_hours_spent", "float8")

    # Since the ticket is not linked anymore, we need to remove the task linked in the timesheets linked to a ticket
    # because the timesheet will not be linked to a task and a ticket at the same time.
    cr.execute(
        """
        UPDATE account_analytic_line
           SET task_id = NULL
         WHERE helpdesk_ticket_id IS NOT NULL
           AND task_id IS NOT NULL
        """
    )
