# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute("""
        UPDATE account_invoice
           SET incoterm_id = incoterms_id
         WHERE incoterm_id IS NULL
           AND incoterms_id IS NOT NULL
    """)

    util.remove_field(cr, "account.invoice", "incoterms_id")
    util.remove_view(cr, 'sale_stock.invoice_form_inherit_sale_stock')
    util.remove_view(cr, "sale_stock.report_invoice_document_inherit_sale_stock")
