# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # Update account_move from existing account_invoice.
    cr.execute('''
        UPDATE purchase_bill_union union
        SET vendor_bill_id = inv.move_id
        FROM account_invoice inv
        WHERE inv.id = union.vendor_bill_id;
    ''')
    util.remove_column(cr, 'purchase_bill_union', 'vendor_bill_id_old')

    # Remove views.
    util.remove_view(cr, 'purchase.view_invoice_supplier_purchase_form')
    util.remove_view(cr, 'purchase.view_invoice_line_form_inherit_purchase')
