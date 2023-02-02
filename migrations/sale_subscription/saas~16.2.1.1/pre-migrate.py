# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "sale.order", "show_rec_invoice_button")
