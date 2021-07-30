# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "account_analytic_account", "group_id", "int4")
    util.create_column(cr, "account_analytic_line", "group_id", "int4")
    util.create_column(cr, "account_analytic_line", "currency_id", "int4")
    cr.execute(
        """
        UPDATE account_analytic_line l
           SET currency_id = c.currency_id
          FROM res_company c
         WHERE c.id = l.company_id
    """
    )

    util.remove_field(cr, "account.analytic.account", "tag_ids")
