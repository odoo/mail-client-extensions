# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    cr.execute("DROP VIEW IF EXISTS sale_subscription_report CASCADE")
    util.remove_constraint(cr, "sale_order", "sale_subscription_stage_coherence")
    util.create_column(cr, "sale_order_log", "origin_order_id", "int4")
    util.create_column(cr, "sale_order_log", "amount_contraction", "numeric")
    util.create_column(cr, "sale_order_log", "amount_expansion", "numeric")
    util.remove_field(cr, "sale.order.log", "amount_company_currency")
    util.remove_field(cr, "sale.order.log", "company_currency_id")

    util.explode_execute(
        cr,
        """UPDATE sale_order_log log
              SET
                  origin_order_id=COALESCE(so.origin_order_id,so.id),
                  amount_contraction=
                    CASE
                        WHEN amount_signed < 0 THEN amount_signed
                        ELSE 0
                    END,
                  amount_expansion=
                    CASE
                        WHEN amount_signed >= 0 THEN 0
                        ELSE amount_signed
                    END
                  event_type = CASE event_type
                    WHEN '1_change' THEN
                      CASE WHEN amount_signed < 0 THEN '15_contraction' ELSE '1_expansion' END
                    ELSE event_type
                  END
              FROM sale_order so
             WHERE so.id=log.order_id
        """,
        table="sale_order_log",
        alias="log",
    )

    util.remove_view(cr, "sale_subscription.sale_subscription_report_view_tree")
    util.remove_view(cr, "sale_subscription.view_subcription_report_graph")
    util.remove_view(cr, "sale_subscription.view_subcription_report_pivot")
    util.remove_record(cr, "sale_subscription.menu_sale_subscription_report_pivot")
    util.remove_record(cr, "sale_subscription.sale_subscription_report_pivot_action")
    util.remove_view(cr, "sale_subscription.sale_order_log_view_graph")
    util.remove_view(cr, "sale_subscription.sale_order_log_view_tree")
    util.remove_record(cr, "sale_subscription.action_sale_order_log")
