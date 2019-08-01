# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "sale_subscription", "recurring_invoice_day", "int4")
    cr.execute(
        """
        UPDATE sale_subscription
           SET recurring_invoice_day = date_part('day', COALESCE(recurring_next_date, date_start))
    """
    )
