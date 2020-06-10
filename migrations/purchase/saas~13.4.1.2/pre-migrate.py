# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
UPDATE purchase_order
   SET date_planned = expected_date
 WHERE date_planned IS NULL
        """
    )

    util.remove_field(cr, "purchase.order", "expected_date")
