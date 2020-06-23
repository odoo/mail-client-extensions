# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "sale_subscription_line", "company_id", "int4")
    cr.execute(
        """
        UPDATE sale_subscription_line l
           SET company_id = a.company_id
          FROM account_analytic_account a
         WHERE a.id = l.analytic_account_id
    """
    )
