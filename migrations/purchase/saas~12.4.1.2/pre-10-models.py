# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute("DROP VIEW IF EXISTS purchase_report")

    util.create_column(cr, "account_move", "purchase_id", "int4")
    util.create_column(cr, "account_move", "purchase_vendor_bill_id", "int4")

    util.create_column(cr, "account_move_line", "purchase_line_id", "int4")

    # Fixing foreign keys and datas is already done by account migration script
    cr.execute("ALTER TABLE account_invoice_purchase_order_rel RENAME TO account_move_purchase_order_rel")
    util.create_column(cr, "account_move_purchase_order_rel", "account_move_id", "int4")

    util.drop_depending_views(cr, "purchase_order", "date_approve")
    cr.execute("ALTER TABLE purchase_order ALTER COLUMN date_approve TYPE timestamp without time zone")

    util.create_column(cr, "purchase_order", "currency_rate", "float8")
    cr.execute(
        """
        UPDATE purchase_order po
           SET currency_rate=1
          FROM res_company c
         WHERE po.company_id=c.id
           AND po.currency_id=c.currency_id
        """
    )

    # reports
    for field in {"unit_quantity", "negociation", "price_standard"}:
        util.remove_field(cr, "purchase.report", field)
