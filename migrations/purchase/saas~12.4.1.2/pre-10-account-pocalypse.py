# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # Columns.
    util.rename_column('purchase_bill_union', 'vendor_bill_id', 'vendor_bill_id_old')
    util.create_column(cr, "purchase_bill_union", "vendor_bill_id", "int4")

    # Views.
    util.remove_view(cr, 'purchase.view_invoice_supplier_purchase_form')
    util.remove_view(cr, 'purchase.view_invoice_line_form_inherit_purchase')
