# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "helpdesk.ticket", "invoice_status")
    util.remove_field(cr, "helpdesk.ticket", "display_create_invoice_primary")
    util.remove_field(cr, "helpdesk.ticket", "display_create_invoice_secondary")
