# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "sale.order", "remaining_validity_days")
    util.move_field_to_module(cr, "sale.order", "tag_ids", "sale_crm", "sale")
    util.create_column(cr, "sale_order", "currency_id", "int4")

    util.explode_execute(
        cr,
        """
        UPDATE sale_order s
           SET currency_id = p.currency_id
          FROM product_pricelist p
         WHERE p.id = s.pricelist_id
        """,
        table="sale_order",
        alias="s",
    )

    gone = """
        access_sale_order_invoicing_payments_readonly
        access_sale_order_line_invoicing_payments_readonly
        access_account_journal_sale_manager
    """
    for xid in util.splitlines(gone):
        util.remove_record(cr, f"sale.{xid}")
