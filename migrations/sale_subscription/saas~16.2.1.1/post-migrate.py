from odoo.upgrade import util


def migrate(cr, version):
    # Handle rating email on stage
    env = util.env(cr)
    cr.execute(
        """
            SELECT name->>'en_US',
                   category,
                   rating_template_id
              FROM sale_order_stage
             WHERE rating_template_id IS NOT NULL
        """
    )
    alert_create_vals = []
    for name, category, mail_template_id in cr.fetchall():
        # create sale.order.alert to send email upon state change
        alert_create_vals.append(
            {
                "name": f"Upgraded Rating action for stage {name}",
                "trigger_condition": "on_create_or_write",
                "action": "mail_post",
                "template_id": mail_template_id,
                "subscription_state": category,
            }
        )
    env["sale.order.alert"].create(alert_create_vals)
    cr.execute("DROP TABLE sale_order_stage CASCADE")

    action_id = util.ref(cr, "sale_subscription.account_analytic_cron_ir_actions_server")
    if action_id:
        cr.execute(
            """
            UPDATE ir_act_server
               SET code = 'model._cron_subscription_expiration()'
             WHERE id = %s
        """,
            [action_id],
        )
    query = "SELECT id FROM sale_order WHERE is_subscription = 't' OR subscription_state = '7_upsell'"
    util.recompute_fields(cr, "sale.order", ["recurring_monthly"], query=query)
