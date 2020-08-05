# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "helpdesk.ticket", "invoice_status")
    util.remove_field(cr, "helpdesk.ticket", "display_create_invoice_primary")
    util.remove_field(cr, "helpdesk.ticket", "display_create_invoice_secondary")

    util.remove_view(cr, "helpdesk_sale_timesheet.helpdesk_tickets_view_search_inherit_helpdesk_sale_timesheet")
    util.remove_record(cr, "helpdesk_sale_timesheet.project_task_server_action_batch_invoice_helpdesk")
