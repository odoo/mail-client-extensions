# -*- coding: utf-8 -*-

def migrate(cr, version):
    # delete old crons
    cr.execute("""
        DELETE FROM ir_cron
              WHERE model = 'subscription.subscription'
                AND id NOT IN (SELECT cron_id FROM subscription_subscription)
    """)

    cr.execute("""
        UPDATE subscription_subscription
           SET cron_id = NULL,
               state = CASE WHEN state='running' THEN 'draft'
                            ELSE state
                        END
         WHERE cron_id NOT IN (select id FROM ir_cron WHERE model='subscription.subscription')
    """)
