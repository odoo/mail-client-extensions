from odoo.upgrade import util


def migrate(cr, version):
    if util.module_installed(cr, "project_sale_subscription"):
        util.move_field_to_module(
            cr, "account.analytic.account", "subscription_count", "sale_subscription", "project_sale_subscription"
        )
        util.move_field_to_module(
            cr, "account.analytic.account", "subscription_ids", "sale_subscription", "project_sale_subscription"
        )
        util.rename_xmlid(
            cr,
            "sale_subscription.account_analytic_account_view_inherit_sale_subscription",
            "project_sale_subscription.account_analytic_account_view_inherit_project_sale_subscription",
        )
    else:
        util.remove_field(cr, "account.analytic.account", "subscription_count")
        util.remove_field(cr, "account.analytic.account", "subscription_ids")
        util.remove_view(cr, "sale_subscription.account_analytic_account_view_inherit_sale_subscription")

    util.remove_record(cr, "sale_subscription.model_sale_order_subscription_cancel")
    util.remove_view(cr, "sale_subscription.sale_subscription_plan_search")
    util.rename_xmlid(
        cr, "sale_subscription.sale_subscription_plan_view_search", "sale_subscription.sale_subscription_plan_search"
    )

    util.remove_record(cr, "sale_subscription.sale_subscription_plan_action")
    util.rename_xmlid(
        cr, "sale_subscription.sale_subscription_action_plan", "sale_subscription.sale_subscription_plan_action"
    )

    util.create_column(
        cr, "sale_order_log", "plan_id", "int4", fk_table="sale_subscription_plan", on_delete_action="RESTRICT"
    )
    util.explode_execute(
        cr,
        """
        UPDATE sale_order_log l
           SET plan_id = o.plan_id
          FROM sale_order o
         WHERE o.id = l.order_id
           AND o.plan_id IS NOT NULL
        """,
        table="sale_order_log",
        alias="l",
    )
