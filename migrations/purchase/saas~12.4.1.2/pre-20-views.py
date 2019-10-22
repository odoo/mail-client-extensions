# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_view(cr, "purchase.view_invoice_supplier_purchase_form")
    util.remove_view(cr, "purchase.view_invoice_line_form_inherit_purchase")
