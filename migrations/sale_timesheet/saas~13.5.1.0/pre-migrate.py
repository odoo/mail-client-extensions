# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "sale.advance.payment.inv", "date_invoice_timesheet")
    util.create_column(cr, "sale_advance_payment_inv", "date_start_invoice_timesheet", "date")
    util.create_column(cr, "sale_advance_payment_inv", "date_end_invoice_timesheet", "date")
