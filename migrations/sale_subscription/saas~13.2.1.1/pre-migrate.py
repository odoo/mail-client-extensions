# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.create_column(cr, "sale_subscription", "fiscal_position_id", "integer")
    util.create_column(cr, "sale_subscription", "stage_category", "varchar")  # fill in `end-`
    util.create_column(cr, "sale_subscription", "payment_term_id", "integer")
    util.remove_field(cr, "sale.subscription", "in_progress")
    for suffix in ["tax{,}", "total{,_incl}"]:
        suffix_from, suffix_to = eb(suffix)
        util.rename_field(cr, "sale.subscription", f"recurring_amount_{suffix_from}", f"recurring_{suffix_to}")
        util.create_column(cr, "sale_subscription", f"recurring_{suffix_to}", "float8")

    cr.execute("DELETE FROM sale_subscription_line WHERE analytic_account_id IS NULL")
    util.create_column(cr, "sale_subscription_line", "price_tax", "float8")
    util.create_column(cr, "sale_subscription_line", "price_total", "float8")
    util.create_column(cr, "sale_subscription_line", "currency_id", "integer")
    util.parallel_execute(
        cr,
        util.explode_query(
            cr,
            """
            UPDATE sale_subscription_line l
               SET currency_id = p.currency_id
              FROM sale_subscription s
              JOIN product_pricelist p ON p.id = s.pricelist_id
             WHERE s.id = l.analytic_account_id
        """,
        prefix="l.",
    ),
    )

    util.create_m2m(cr, "account_tax_sale_subscription_line_rel", "account_tax", "sale_subscription_line")
    cr.execute(
        """
        INSERT INTO account_tax_sale_subscription_line_rel(account_tax_id, sale_subscription_line_id)
             SELECT r.tax_id, l.id
               FROM sale_subscription_line l
               JOIN product_product p ON p.id = l.product_id
               JOIN product_taxes_rel r ON r.prod_id = p.product_tmpl_id
    """
    )

    util.create_column(cr, "sale_subscription_stage", "category", "varchar")
    cr.execute(
        """
        UPDATE sale_subscription_stage
           SET category = CASE in_progress WHEN true THEN 'progress' ELSE 'closed' END
    """
    )
    util.remove_field(cr, "sale.subscription.stage", "in_progress")
    # Do not update name & sequence of builtin stages.
    # We should also keep `to upsell` as we don't know if it is in use in the current database.
    cr.execute(
        """
            UPDATE ir_model_data
               SET noupdate = true
             WHERE model = 'sale.subscription.stage'
               AND module = 'sale_subscription'
        """
    )

    util.rename_model(cr, "sale.subscription.snapshot", "sale.subscription.log")
    util.rename_field(cr, "sale.subscription.log", "date", "event_date")

    new_fields = [
        ("event_type", "varchar"),
        ("category", "varchar"),
        ("user_id", "integer"),
        ("team_id", "integer"),
        ("amount_signed", "numeric"),
        ("currency_id", "integer"),
        ("amount_company_currency", "numeric"),
        ("company_currency_id", "integer"),
        ("company_id", "integer"),
    ]
    for name, type_ in new_fields:
        util.create_column(cr, "sale_subscription_log", name, type_)

    cr.execute(
        """
        UPDATE sale_subscription_log l
           SET event_type = '1_change',
               category = 'progress',
               currency_id = p.currency_id,  -- ??
               company_currency_id = c.currency_id,
               company_id = c.id
          FROM sale_subscription s
          JOIN product_pricelist p ON p.id = s.pricelist_id
          JOIN res_company c ON c.id = s.company_id
         WHERE s.id = l.subscription_id
    """
    )

    util.remove_field(cr, "sale.subscription.report", "in_progress")

    util.remove_record(cr, "sale_subscription.access_sale_subscription_snapshot")
