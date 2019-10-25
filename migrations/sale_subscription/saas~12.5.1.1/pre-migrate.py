# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "sale_subscription_line", "company_id", "int4")
    util.create_column(cr, "sale_subscription_template", "company_id", "int4")

    cr.execute(
        """
        UPDATE sale_subscription_line l
           SET company_id=s.company_id
          FROM sale_subscription s
         WHERE s.id=l.analytic_account_id
           AND l.company_id IS NULL
        """
    )
