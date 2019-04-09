# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute("UPDATE account_payment SET name='' WHERE state='draft' and name='Draft Payment'")

    util.rename_xmlid(cr, "sale.group_show_price_subtotal", "account.group_show_line_subtotals_tax_excluded")
    util.rename_xmlid(cr, "sale.group_show_price_total", "account.group_show_line_subtotals_tax_included")
    cr.execute("""
        UPDATE ir_config_parameter
           SET value = CASE value WHEN 'total' THEN 'tax_included'
                                  ELSE 'tax_excluded'
                        END,
               key = 'account.show_line_subtotals_tax_selection'
         WHERE key = 'sale.sale_show_tax'
    """)
