# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute("DROP VIEW IF EXISTS purchase_report")

    util.create_column(cr, "account_move", "purchase_id", "int4")
    util.create_column(cr, "account_move", "purchase_vendor_bill_id", "int4")

    util.create_column(cr, "account_move_line", "purchase_line_id", "int4")
    cr.execute(
        """
        UPDATE account_move_line aml
           SET purchase_line_id=inv.purchase_line_id
          FROM account_invoice_line inv
    INNER JOIN invl_aml_mapping map ON map.invl_id=inv.id
    INNER JOIN purchase_order_line pol ON pol.id=inv.purchase_line_id
         WHERE aml.id = map.aml_id AND map.is_invoice_line IS TRUE;
        """
    )

    #Fixing foreign keys and datas is already done by account migration script
    cr.execute("ALTER TABLE account_invoice_purchase_order_rel RENAME TO account_move_purchase_order_rel")
    cr.execute("ALTER TABLE account_move_purchase_order_rel RENAME COLUMN account_invoice_id TO account_move_id")

    cr.execute("ALTER TABLE purchase_order ALTER COLUMN date_approve TYPE timestamp without time zone")

    # util.create_m2m(cr, "account_invoice_purchase_order_rel", "purchase_order", "account_move")
    # cr.execute(
    #     """
    #     INSERT INTO account_invoice_purchase_order_rel (purchase_order_id, account_move_id)
    #          SELECT po.id, aml.move_id
    #            FROM purchase_order po
    #      INNER JOIN purchase_order_line pol on pol.order_id=po.id
    #      INNER JOIN account_move_line aml on aml.purchase_line_id=pol.id
    #     """
    # )
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
