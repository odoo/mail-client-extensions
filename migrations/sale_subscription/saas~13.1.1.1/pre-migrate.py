# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "sale_subscription_line", "company_id", "int4")
    cr.execute(
        """
        UPDATE sale_subscription_line l
           SET company_id = s.company_id
          FROM sale_subscription s
         WHERE s.id = l.analytic_account_id
    """
    )
