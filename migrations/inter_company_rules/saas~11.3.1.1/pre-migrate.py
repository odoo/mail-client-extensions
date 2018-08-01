# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "res_company", "rule_type", "varchar")
    util.create_column(cr, "res_company", "applicable_on", "varchar")

    cr.execute("""
        UPDATE res_company
           SET rule_type = CASE WHEN so_from_po=true OR po_from_so=true OR auto_validation=true
                                THEN 'so_and_po'
                                WHEN auto_generate_invoices=true
                                THEN 'invoice_and_refund'
                                ELSE NULL
                            END,
              applicable_on = CASE WHEN so_from_po=true AND po_from_so=true
                                   THEN 'sale_purchase'
                                   WHEN so_from_po=true
                                   THEN 'sale'
                                   WHEN po_from_so=true
                                   THEN 'purchase'
                              END
    """)
    cr.execute("""
        ALTER TABLE res_company
       ALTER COLUMN auto_validation
               TYPE varchar
              USING CASE WHEN auto_validation=true THEN 'validated' ELSE 'draft' END
    """)

    util.remove_field(cr, "res.company", "so_from_po")
    util.remove_field(cr, "res.company", "po_from_so")
    util.remove_field(cr, "res.company", "auto_generate_invoices")

    util.remove_field(cr, "res.config.settings", "so_from_po")
    util.remove_field(cr, "res.config.settings", "po_from_so")
    util.remove_field(cr, "res.config.settings", "auto_validation")
