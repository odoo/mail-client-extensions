from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "base_automation", "is_sale_order_alert", "boolean")
    cr.execute(
        """
            WITH soa AS (
                 SELECT automation_id
                   FROM sale_order_alert
                  WHERE automation_id IS NOT NULL
               GROUP BY automation_id
            )
            UPDATE base_automation a
               SET is_sale_order_alert = true
              FROM soa
             WHERE a.id = soa.automation_id
        """
    )

    util.create_column(
        cr, "sale_order_alert", "action_id", "integer", fk_table="ir_act_server", on_delete_action="RESTRICT"
    )
    cr.execute(
        """
            WITH actions AS (
                SELECT ias.id,
                       ias.base_automation_id
                  FROM ir_act_server AS ias
                       INNER JOIN base_automation AS ba
                       ON ba.id = ias.base_automation_id
                 WHERE ba.is_sale_order_alert = true
            )
            UPDATE sale_order_alert
               SET action_id = act.id
              FROM actions AS act
             WHERE automation_id = act.base_automation_id
        """
    )

    util.remove_field(cr, "sale.order.log.report", "recurring_yearly_graph")
    util.remove_field(cr, "sale.order.log.report", "recurring_monthly_graph")
    util.remove_field(cr, "sale.order.log.report", "amount_signed_graph")

    util.remove_view(cr, "sale_subscription.payment_checkout_inherit")

    util.remove_field(cr, "sale.order.log", "amount_expansion")
    util.remove_field(cr, "sale.order.log", "amount_contraction")

    util.delete_unused(cr, "sale_subscription.mail_template_subscription_invoice")

    # Journal
    cr.execute(
        r"""
    UPDATE sale_order
       SET journal_id = REPLACE(ip.value_reference, 'account.journal,', '')::int
      FROM ir_property ip
     WHERE ip.res_id = 'sale.order.template,' || sale_order.sale_order_template_id
       AND sale_order.company_id = ip.company_id
       AND ip.name = 'journal_id'
       AND ip.value_reference ~ 'account\.journal,\d+'
       AND ip.res_id LIKE 'sale.order.template,%'
        """
    )

    # Template
    util.create_column(cr, "sale_order_template", "is_unlimited", "boolean")
    cr.execute(
        """
    UPDATE sale_order_template
       SET is_unlimited = true
     WHERE recurring_rule_boundary = 'unlimited'
        """
    )

    # update sale_order_template_id for subscription-related sale orders
    util.explode_execute(
        cr,
        """
        UPDATE sale_order AS so
           SET sale_order_template_id = parent_sub.sale_order_template_id
          FROM sale_order AS parent_sub
         WHERE so.subscription_id = parent_sub.id
           AND so.sale_order_template_id IS NULL
           AND so.subscription_state = '7_upsell'
           AND parent_sub.sale_order_template_id IS NOT NULL
        """,
        table="sale_order",
        alias="so",
    )

    cr.execute(
        """
    CREATE TABLE sale_subscription_plan (
        id SERIAL NOT NULL PRIMARY KEY,
        company_id int4,
        billing_period_value int4 NOT NULL,
        auto_close_limit int4,
        invoice_mail_template_id int4,
        user_closable boolean,
        billing_period_unit varchar NOT NULL,
        name varchar NOT NULL,
        template_id int4,
        recurrence_id int4,
        active boolean,
        pause boolean
        )
        """
    )

    # Create new plan based on usage in SO and Template/Recurrence values
    cr.execute(
        """
           WITH combination AS (
                SELECT sale_order_template_id,
                       recurrence_id
                  FROM sale_order
                 WHERE is_subscription
                   AND recurrence_id IS NOT NULL
              GROUP BY sale_order_template_id,
                       recurrence_id
                )
    INSERT INTO sale_subscription_plan (
                name,
                billing_period_unit,
                billing_period_value,
                user_closable,
                auto_close_limit,
                company_id,
                invoice_mail_template_id,
                template_id,
                recurrence_id,
                active,
                pause
            )
         SELECT COALESCE(sot.name, str.duration || ' ' || str.unit) AS name,
                CASE str.unit
                    WHEN 'day' THEN 'week'
                    WHEN 'hour' THEN 'week'
                    ELSE str.unit
                END AS billing_period_unit,
                CASE str.unit
                    WHEN 'day' THEN CEIL(str.duration / 7)
                    WHEN 'hour' THEN CEIL(str.duration / 24 / 7)
                    ELSE str.duration
                END AS billing_period_value,
                COALESCE(sot.user_closable, false) AS user_closable,
                COALESCE(sot.auto_close_limit, 15) AS auto_close_limit,
                sot.company_id AS company_id,
                COALESCE(sot.invoice_mail_template_id, %s) AS invoice_mail_template_id,
                sot.id AS template_id,
                str.id AS recurrence_id,
                COALESCE(str.active, false) AND COALESCE(sot.active, false) AS active,
                str.unit IN ('day', 'hour') AS pause
           FROM combination
      LEFT JOIN sale_order_template sot ON sot.id = combination.sale_order_template_id
           JOIN sale_temporal_recurrence str ON str.id = combination.recurrence_id;
        """,
        [util.ref(cr, "account.email_template_edi_invoice")],
    )

    # Update reference on Template
    util.create_column(
        cr, "sale_order_template", "plan_id", "integer", fk_table="sale_subscription_plan", on_delete_action="SET NULL"
    )
    cr.execute(
        """
    UPDATE sale_order_template sot
       SET plan_id = ssp.id
      FROM sale_subscription_plan ssp
     WHERE ssp.recurrence_id = sot.recurrence_id
       AND ssp.template_id = sot.id
        """
    )

    # Update reference on SO
    util.create_column(
        cr, "sale_order", "plan_id", "integer", fk_table="sale_subscription_plan", on_delete_action="RESTRICT"
    )
    util.explode_execute(
        cr,
        """
    UPDATE sale_order so
       SET plan_id = ssp.id
      FROM sale_subscription_plan ssp
     WHERE so.recurrence_id = ssp.recurrence_id
       AND ssp.template_id IS NOT DISTINCT FROM so.sale_order_template_id
        """,
        table="sale_order",
        alias="so",
    )

    cr.execute(
        """
    UPDATE sale_order so
       SET subscription_state = '4_paused'
      FROM sale_subscription_plan ssp
     WHERE so.recurrence_id = ssp.recurrence_id
       AND ssp.pause
       AND so.subscription_state in ('3_progress', '4_paused')
 RETURNING so.id, so.name
        """,
    )
    so_ids = cr.fetchall()
    if so_ids:
        util.add_to_migration_reports(
            """
            <details>
                <summary>
                    The following subscriptions have been paused because their recurrence was hourly/daily which is not supported anymore.
                </summary>
                <ul>{}</ul>
            </details>
            """.format(
                " ".join(f"<li>{util.get_anchor_link_to_record('sale.order', id, name)}</li>" for id, name in so_ids)
            ),
            category="Subscription",
            format="html",
        )

    # Update reference on company
    if util.column_exists(cr, "res_company", "subscription_default_recurrence_id"):
        util.create_column(
            cr,
            "res_company",
            "subscription_default_plan_id",
            "integer",
            fk_table="sale_subscription_plan",
            on_delete_action="SET NULL",
        )
        cr.execute(
            """
          WITH ssp AS (
                SELECT company_id,
                       recurrence_id,
                       MIN(p.id) AS plan_id
                  FROM sale_subscription_plan p
              GROUP BY company_id,
                       recurrence_id
               )
        UPDATE res_company c
           SET subscription_default_plan_id = ssp.plan_id
          FROM ssp
         WHERE ssp.recurrence_id = c.subscription_default_recurrence_id
           AND c.id = ssp.company_id
            """
        )
        util.remove_field(cr, "res.company", "subscription_default_recurrence_id")

    util.rename_field(cr, "sale.order.template", "recurring_rule_count", "duration_value")
    util.rename_field(cr, "sale.order.template", "recurring_rule_type", "duration_unit")

    # remove column only as field removed in base
    util.remove_column(cr, "sale_order", "recurrence_id")

    util.remove_field(cr, "sale.order.line", "temporal_type")
    util.remove_field(cr, "sale.order.log.report", "recurrence_id")
    util.remove_field(cr, "sale.order.template", "user_closable")
    util.remove_field(cr, "sale.order.template", "auto_close_limit")
    util.remove_field(cr, "sale.order.template", "recurrence_id")
    util.remove_field(cr, "sale.order.template", "invoice_mail_template_id")
    util.remove_field(cr, "sale.order.template", "recurring_rule_boundary")
    util.remove_field(cr, "sale.order.template.line", "recurrence_id")
    util.remove_field(cr, "sale.order.template.option", "recurrence_id")
    util.remove_field(cr, "sale.subscription.report", "recurrence_id")
    util.remove_field(cr, "res.config.settings", "subscription_default_recurrence_id")

    util.remove_view(cr, "sale_subscription.sale_subscription_recurrence_search")
    util.remove_record(cr, "sale_subscription.sale_subscription_recurrence_action")
    util.remove_view(cr, "sale_subscription.subscription")
    util.remove_view(cr, "sale_subscription.payment_portal_breadcrumb_inherit")
