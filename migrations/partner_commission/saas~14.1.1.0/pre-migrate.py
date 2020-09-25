# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "purchase_order", "purchase_type", "varchar", default="procurement")

    # Populate purchase_type:
    # a purchase_order of type 'commission' should have one of its purchase_order_line
    # referenced by an account_move, via the commission_po_line_id foreign key.
    # Otherwise, the purchase_type should be set to 'procurement'.
    cr.execute(
        """
        UPDATE purchase_order po
           SET purchase_type = 'commission'
          FROM purchase_order_line pol
          JOIN account_move am ON pol.id = am.commission_po_line_id
         WHERE pol.order_id = po.id
    """
    )
