# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "helpdesk_ticket", "sale_line_id", "int4")
    util.remove_field(cr, "helpdesk.ticket", "display_create_so_button_primary")
    util.remove_field(cr, "helpdesk.ticket", "display_create_so_button_secondary")
    util.remove_field(cr, "helpdesk.ticket", "sale_line_id_source")

    # Remove view from helpdesk_sale_timesheet_edit (module merged with helpdesk_sale_timesheet)
    util.remove_view(cr, "helpdesk_sale_timesheet.helpdesk_ticket_view_form_inherit_helpdesk_sale_timesheet_edit")
    util.create_m2m(cr, "helpdesk_sla_sale_order_line_rel", "helpdesk_sla", "sale_order_line")
