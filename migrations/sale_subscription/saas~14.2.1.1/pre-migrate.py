# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute(
        """
            UPDATE sale_subscription_template
               SET payment_mode = 'validate_send'
             WHERE payment_mode = 'validate_send_payment'
        """
    )
