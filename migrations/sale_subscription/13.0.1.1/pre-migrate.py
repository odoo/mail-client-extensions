# -*- coding: utf-8 -*-

def migrate(cr, version):
    # see https://github.com/odoo/enterprise/pull/10863
    cr.execute(
        """
        DELETE FROM sale_subscription_line
         WHERE analytic_account_id IS NULL
        """
    )
