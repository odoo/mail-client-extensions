# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.rename_xmlid(
        cr, "sale_stock.sale_stock_report_invoice_document", "stock_account.stock_account_report_invoice_document"
    )
    util.rename_xmlid(cr, *util.expand_braces("{sale_stock,stock_account}.group_lot_on_invoice"))
    util.move_field_to_module(cr, "res.config.settings", "group_lot_on_invoice", "sale_stock", "stock_account")
