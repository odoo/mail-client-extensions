# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "helpdesk_sale_timesheet.helpdesk_ticket_view_form_inherit_helpdesk_sale_timesheet_editable")
    util.remove_view(cr, "helpdesk_sale_timesheet.product_template_form_view_invoice_policy_inherit_helpdesk_user")
