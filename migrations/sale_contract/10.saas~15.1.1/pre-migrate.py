# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'sale_subscription', 'recurring_monthly', 'double precision')
    cr.execute("""
        UPDATE sale_subscription s
           SET recurring_monthly = s.recurring_total * (CASE
                    WHEN t.recurring_rule_type = 'daily' THEN 30.0
                    WHEN t.recurring_rule_type = 'weekly' THEN 30.0 / 7.0
                    WHEN t.recurring_rule_type = 'monthly' THEN 1.0
                    WHEN t.recurring_rule_type = 'yearly' THEN 1.0 / 12.0
                    END) / t.recurring_interval
          FROM sale_subscription_template t
         WHERE t.id = s.template_id
    """)
