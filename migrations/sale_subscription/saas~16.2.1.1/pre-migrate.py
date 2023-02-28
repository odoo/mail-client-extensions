# -*- coding: utf-8 -*-

from odoo.osv import expression

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "sale.order", "show_rec_invoice_button")
    util.create_column(cr, "sale_order", "recurring_total", "numeric")
    util.create_column(cr, "sale_order", "subscription_state", "varchar")
    util.create_column(cr, "sale_order_log", "subscription_state", "varchar")

    # Set subscription_state based on the subscription stage and order_state
    state_query = """
UPDATE sale_order so
   SET subscription_state =
    CASE
        WHEN so.subscription_management = 'renew'
         AND so.subscription_id IS NOT NULL
         AND st.category = 'draft'                              THEN '2_renewal'
        WHEN st.category = 'draft'                              THEN '1_draft'
        WHEN so.state = 'done'
         AND st.category IN ('closed', 'progress', 'paused')    THEN '5_renewed'
        WHEN st.category = 'progress'                           THEN '3_progress'
        WHEN st.category = 'paused'                             THEN '4_paused'
        WHEN st.category = 'closed'                             THEN '6_churn'
     END
  FROM sale_order_stage st
 WHERE st.id = so.stage_id
   AND so.is_subscription = true
    """
    util.explode_execute(cr, state_query, table="sale_order", alias="so")

    # Set subscription_state for upsell
    upsell_query = """
UPDATE sale_order so
   SET subscription_state = '7_upsell'
 WHERE subscription_management = 'upsell'
    """
    util.explode_execute(cr, upsell_query, table="sale_order", alias="so")

    # Compute recurring_total
    recurring_total_query = """
  WITH lines AS (
    SELECT l.order_id,
           SUM(l.price_subtotal) AS sum_recurring
      FROM sale_order_line l
      JOIN product_product p
        ON l.product_id = p.id
      JOIN product_template t
        ON p.product_tmpl_id = t.id
      JOIN sale_order so
        ON so.id = l.order_id
     WHERE t.recurring_invoice
       AND {parallel_filter}
       AND so.is_subscription
  GROUP BY l.order_id
)
UPDATE sale_order so
   SET recurring_total = lines.sum_recurring
  FROM lines
 WHERE lines.order_id = so.id
    """
    util.explode_execute(cr, recurring_total_query, table="sale_order", alias="so")

    # Set subscription_state for sale.order.log
    log_state_query = """
 UPDATE sale_order_log log
    SET subscription_state = CASE log.state_category
        WHEN 'draft'    THEN '1_draft'
        WHEN 'progress' THEN '3_progress'
        WHEN 'paused'   THEN '4_paused'
        WHEN 'closed'   THEN '6_churn'
        ELSE '3_progress'
      END
    """
    util.explode_execute(cr, log_state_query, table="sale_order_log", alias="log")

    # Delete alert with action removed
    cr.execute("SELECT id FROM sale_order_alert WHERE action IN ('set_stage', 'set_to_renew')")
    util.remove_records(cr, "sale.order.alert", [aid for aid, in cr.fetchall()])

    util.remove_view(cr, "sale_subscription.sale_order_view_tree_subscription")
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("sale_subscription.subtype_sta{g,t}e_change"))

    def adapter_stage_category(leaf, is_or, negated):
        _, op, right = leaf
        new_right = []

        if "draft" in right:
            new_right += ["1_draft", "2_renewal"]
        if "progress" in right:
            new_right += ["3_progress"]
        if "paused" in right:
            new_right += ["4_paused"]
        if "closed" in right:
            new_right += ["5_renewed", "6_churn"]

        if not len(new_right):
            if is_or ^ negated:
                return [expression.FALSE_LEAF]
            return [expression.TRUE_LEAF]

        if op in ["=", "in"]:
            new_op = "in" if len(new_right) > 1 else "="
        else:
            new_op = "not in" if len(new_right) > 1 else "!="

        new_right = new_right[0] if len(new_right) == 1 else new_right
        return [("subscription_state", new_op, new_right)]

    util.adapt_domains(cr, "sale.order", "stage_category", "subscription_state", adapter=adapter_stage_category)

    def adapter_management(leaf, is_or, negated):
        _, op, right = leaf
        new_right = []

        if "upsell" in right:
            new_right += ["7_upsell"]
        if "renew" in right:
            new_right += ["2_renewal"]

        if not len(new_right):
            if is_or ^ negated:
                return [expression.FALSE_LEAF]
            return [expression.TRUE_LEAF]

        if op in ["=", "in"]:
            new_op = "in" if len(new_right) > 1 else "="
        else:
            new_op = "not in" if len(new_right) > 1 else "!="

        new_right = new_right[0] if len(new_right) == 1 else new_right
        return [("subscription_state", new_op, new_right)]

    util.adapt_domains(cr, "sale.order", "subscription_management", "subscription_state", adapter=adapter_management)

    util.remove_field(cr, "sale.order", "renew_state")
    util.remove_field(cr, "sale.order", "recurring_live")
    util.remove_field(cr, "sale.order", "to_renew")
    util.remove_field(cr, "sale.order", "stage_id")
    util.remove_field(cr, "sale.order", "stage_category")
    util.remove_field(cr, "sale.order", "subscription_management")
    util.remove_field(cr, "sale.order.log", "category")
    util.remove_field(cr, "sale.order.alert", "stage_category")
    util.remove_field(cr, "sale.order.alert", "stage_id")
    util.remove_field(cr, "sale.order.alert", "stage_to_id")
    util.remove_field(cr, "sale.order.alert", "stage_from_id")
    util.remove_field(cr, "sale.subscription.report", "stage_id")
    util.remove_field(cr, "sale.subscription.report", "stage_category")
    util.remove_field(cr, "sale.subscription.report", "to_renew")
    util.remove_field(cr, "sale.subscription.report", "quantity")
    util.remove_field(cr, "sale.subscription.report", "date_order")

    util.remove_record(cr, "sale_subscription.sale_subscription_action_res_partner")
    util.remove_record(cr, "sale_subscription.menu_sale_subscription_stage")

    # Handling rating mail on stages in post. We need to keep the table
    util.remove_model(cr, "sale.order.stage", drop_table=False)
