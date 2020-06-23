# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        INSERT INTO approval_product_line(approval_request_id, description, quantity)
             SELECT id, items, 1
               FROM approval_request
              WHERE items IS NOT NULL
    """
    )

    util.remove_field(cr, "approval.request", "items")
    util.remove_field(cr, "approval.request", "has_item")
