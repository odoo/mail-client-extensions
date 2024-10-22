from odoo.upgrade import util


def migrate(cr, version):
    # Ensure existing in progress subscriptions are processed by the _cron_recurring_create_invoice
    # This ensure the previous behavior is kept
    util.explode_execute(
        cr,
        """
            UPDATE sale_order
               SET require_payment=False
             WHERE subscription_state IN ('3_progress', '4_paused')
               AND payment_token_id is NULL
            """,
        table="sale_order",
        alias="so",
    )
