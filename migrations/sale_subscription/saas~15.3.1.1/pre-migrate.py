import logging

from psycopg2.extras import Json

from odoo import models

from odoo.addons.sale_subscription.models import sale_order_stage as _ignore  # noqa

from odoo.upgrade import util

NS = "openerp.addons.base.maintenance.migrations.sale_subscription.saas-15.3."
_logger = logging.getLogger(NS + __name__)


def migrate(cr, version):
    util.remove_field(cr, "sale.order", "subscription_count")
    util.remove_view(cr, "sale_subscription.sale_subscription_order_form_view")
    util.create_column(cr, "sale_order_template", "recurring_rule_type", "varchar")
    util.create_column(cr, "sale_order_template", "recurring_rule_boundary", "varchar")
    util.create_column(cr, "sale_order_template", "recurring_rule_count", "int4")
    util.create_column(cr, "sale_order_template", "user_closable", "boolean")
    util.create_column(cr, "sale_order_template", "auto_close_limit", "int4")
    util.create_column(cr, "sale_order_template", "good_health_domain", "varchar")
    util.create_column(cr, "sale_order_template", "bad_health_domain", "varchar")
    util.create_column(cr, "sale_order_template", "invoice_mail_template_id", "int4")
    # temporary column used to retrieve the tags
    util.create_column(cr, "sale_order_template", "old_template_id", "int4")
    util.create_column(cr, "sale_order_template", "recurrence_id", "int4")

    # In the old system, when a subscription template required a token, the account move was sent by mail after the success payment
    # but the is_move_sent value of these invoice was never true. In the new system, we need to mark these moves as sent to avoid
    # sending all these old account move as soon as the _create_recurring_invoice method is called.
    # We select the account_move created from subscription where the subscription template 'payment_mode' value was
    # 'success_payment' (paid by token). In 15.3, the payment_mode field on template disappears.
    cr.execute(
        """
        UPDATE account_move am
           SET is_move_sent=true
         WHERE am.id IN (SELECT DISTINCT aml.move_id
                                    FROM account_move_line aml
                                    JOIN sale_subscription sub ON sub.id = aml.subscription_id
                                    JOIN sale_subscription_template subtml ON subtml.id = sub.template_id
                                    JOIN account_move move ON move.id = aml.move_id
                                   WHERE move.state = 'posted'
                                     AND move.is_move_sent IS FALSE
                                     AND subtml.payment_mode IN ('validate_send', 'validate_send_payment', 'success_payment'))
        """
    )
    # Rename rule type of template to ease the migration
    util.change_field_selection_values(
        cr,
        "sale.subscription.template",
        "recurring_rule_type",
        {"daily": "day", "weekly": "week", "monthly": "month", "yearly": "year"},
    )
    cr.execute("ALTER TABLE product_pricing ADD COLUMN _mig_sub_line_id integer[]")

    # temporary column used to retrieve easily the recurrence
    cr.execute("ALTER TABLE sale_temporal_recurrence ADD COLUMN _mig_sst_id integer[]")
    # Create recurrence rules defined on SO and pricings
    cr.execute(
        """
        WITH sst AS (  SELECT sst.recurring_interval duration,
                              sst.recurring_rule_type unit,
                              array_agg(sst.id) agg
                         FROM sale_subscription_template sst
                     GROUP BY sst.recurring_interval,
                              sst.recurring_rule_type)
        UPDATE sale_temporal_recurrence str
           SET _mig_sst_id = sst.agg
          FROM sst
         WHERE str.duration = sst.duration
           AND str.unit = sst.unit
        """
    )
    if util.column_exists(cr, "sale_temporal_recurrence", "active"):
        active_field = ", active"
        active_val = ", true"
    else:
        active_field = active_val = ""
    cr.execute(
        f"""
        WITH sst AS (   SELECT sst.recurring_interval duration,
                               sst.recurring_rule_type unit,
                               array_agg(sst.id) agg
                          FROM sale_subscription_template sst
                     LEFT JOIN sale_temporal_recurrence str
                            ON str.duration = sst.recurring_interval
                           AND str.unit = sst.recurring_rule_type
                         WHERE str.id IS NULL
                      GROUP BY sst.recurring_interval,
                               sst.recurring_rule_type)
        INSERT INTO sale_temporal_recurrence (duration, unit, _mig_sst_id {active_field})
        SELECT duration, unit, agg {active_val}
          FROM sst
        """
    )
    cr.commit()
    jsonb_column = util.column_type(cr, "sale_order_template", "note") == "jsonb"
    sst_description = "jsonb_build_object('en_US', sst.description)" if jsonb_column else "sst.description"
    cr.execute(
        f"""
        INSERT INTO sale_order_template (old_template_id,name,active,note,recurring_rule_type,
                                         recurring_rule_boundary,recurring_rule_count,user_closable,auto_close_limit,
                                         good_health_domain,bad_health_domain,invoice_mail_template_id,company_id,recurrence_id)
             SELECT sst.id,CONCAT ('Upgraded ', sst.name),sst.active,{sst_description},sst.recurring_rule_type,
                    sst.recurring_rule_boundary,(sst.recurring_interval * sst.recurring_rule_count),sst.user_closable,sst.auto_close_limit,
                    sst.good_health_domain,sst.bad_health_domain,sst.invoice_mail_template_id,sst.company_id,str.id
               FROM sale_subscription_template sst
               JOIN sale_temporal_recurrence str ON sst.id = ANY (str._mig_sst_id)
        """
    )

    util.create_column(cr, "sale_order", "old_subscription_id", "int4")
    util.create_column(cr, "sale_order", "is_subscription", "boolean")
    util.create_column(cr, "sale_order", "to_renew", "boolean")
    util.create_column(cr, "sale_order", "payment_exception", "boolean")
    util.create_column(cr, "sale_order", "recurring_live", "boolean")
    util.create_column(cr, "sale_order", "rating_last_value", "float8")
    util.create_column(cr, "sale_order", "stage_id", "int4")
    util.create_column(cr, "sale_order", "end_date", "date")
    util.create_column(cr, "sale_order", "close_reason_id", "int4")
    util.create_column(cr, "sale_order", "country_id", "int4")
    util.create_column(cr, "sale_order", "industry_id", "int4")
    util.create_column(cr, "sale_order", "payment_token_id", "int4")
    util.create_column(cr, "sale_order", "subscription_id", "int4")
    util.create_column(cr, "sale_order", "kpi_1month_mrr_delta", "float8")
    util.create_column(cr, "sale_order", "kpi_1month_mrr_percentage", "float8")
    util.create_column(cr, "sale_order", "kpi_3months_mrr_delta", "float8")
    util.create_column(cr, "sale_order", "kpi_3months_mrr_percentage", "float8")
    util.create_column(cr, "sale_order", "percentage_satisfaction", "int4")
    util.create_column(cr, "sale_order", "health", "varchar")
    util.create_column(cr, "sale_order", "stage_category", "varchar")
    util.create_column(cr, "sale_order", "origin_order_id", "int4")
    util.create_column(cr, "sale_order", "recurring_monthly", "numeric")
    util.create_column(cr, "sale_order", "next_invoice_date", "date")
    util.create_column(cr, "sale_order", "start_date", "date")
    util.create_column(cr, "sale_order", "recurrence_id", "int4")

    util.create_column(cr, "sale_order_line", "pricing_id", "int4")
    util.create_column(cr, "sale_order_line", "old_subscription_line_id", "int4")

    cr.execute("CREATE INDEX ON sale_order_line (old_subscription_line_id) WHERE old_subscription_line_id IS NOT NULL")
    util.create_column(cr, "sale_order_line", "old_subscription_id", "int4")
    cr.execute("CREATE INDEX ON sale_order_line (old_subscription_id) WHERE old_subscription_id IS NOT NULL")
    util.create_column(cr, "sale_order_line", "parent_line_id", "int4")

    util.rename_model(cr, "sale.subscription.log", "sale.order.log")
    util.rename_field(cr, "sale.order.log", "subscription_id", "order_id")
    cr.execute("ALTER TABLE sale_order_log RENAME COLUMN order_id TO old_subscription_id")
    util.create_column(cr, "sale_order_log", "order_id", "int4")
    cr.execute("CREATE INDEX ON sale_order_log (order_id, event_date desc, id desc)")

    # We update the rentable subscription product because having a subscription product rented is not supported
    if util.module_installed(cr, "sale_renting"):
        _handle_recurring_renting_products(cr)

    cr.commit()
    # pricing creation
    util.create_column(cr, "product_pricing", "_upg_variant_id", "int4")

    cr.execute(
        """
        INSERT INTO product_pricing (_upg_variant_id,price,recurrence_id,product_template_id,currency_id,pricelist_id,_mig_sub_line_id)
        SELECT DISTINCT ON(pp.id, str.id, pp.product_tmpl_id, ss.pricelist_id) pp.id,ssl.price_unit,str.id,
               pp.product_tmpl_id,ssl.currency_id,
               ss.pricelist_id,array_agg(ssl.id)
          FROM sale_subscription_line ssl
          JOIN product_product pp ON ssl.product_id=pp.id
          JOIN product_template pt ON pp.product_tmpl_id=pt.id
          JOIN sale_subscription ss ON ss.id=ssl.analytic_account_id
          JOIN sale_subscription_template sst ON ss.template_id=sst.id
          JOIN sale_temporal_recurrence str ON sst.id = ANY (str._mig_sst_id)
          GROUP BY pp.id,ssl.price_unit,str.id,pp.product_tmpl_id,ssl.currency_id,ss.pricelist_id,sst.recurring_rule_type
        """
    )
    cr.execute(
        """
        INSERT INTO product_pricing_product_product_rel(product_pricing_id,
product_product_id)
               SELECT id,_upg_variant_id
               FROM product_pricing
               WHERE _upg_variant_id IS NOT NULL
        """
    )
    util.remove_column(cr, "product_pricing", "_upg_variant_id")

    # Update current Quotation SO line with pricings
    util.parallel_execute(
        cr,
        util.explode_query_range(
            cr,
            """
         WITH sols as(
            SELECT sol.id as sol_id,
                   pp.pricing_id
              FROM sale_order_line sol
              JOIN sale_order so ON sol.order_id = so.id
              JOIN product_product p ON p.id = sol.product_id
              JOIN product_template pt ON p.product_tmpl_id=pt.id
              LEFT JOIN LATERAL (
                    SELECT pp.id as pricing_id FROM product_pricing pp WHERE
                   pp.recurrence_id = so.recurrence_id AND
                   pp.product_template_id = p.product_tmpl_id AND
                   pp.currency_id = sol.currency_id
                   LIMIT 1
                   ) AS pp ON TRUE
             WHERE so.state IN ('draft', 'sent')
               AND sol.pricing_id IS NULL
               AND pt.recurring_invoice
               AND so.is_subscription
               AND {parallel_filter}
         )
         UPDATE sale_order_line
            SET pricing_id = sols.pricing_id
           FROM sols
          WHERE sale_order_line.id = sols.sol_id
            """,
            table="sale_order_line",
            alias="sol",
        ),
    )

    # change model of custom fields to sale.order to prevent removal
    model_ids = [
        (
            util.ref(cr, "sale.model_sale_order"),
            util.ref(cr, "sale_subscription.model_sale_subscription"),
            "sale.order",
        ),
        (
            util.ref(cr, "sale.model_sale_order_line"),
            util.ref(cr, "sale_subscription.model_sale_subscription_line"),
            "sale.order.line",
        ),
        (
            util.ref(cr, "sale_management.model_sale_order_template"),
            util.ref(cr, "sale_subscription.model_sale_subscription_template"),
            "sale.order.template",
        ),
    ]
    manual_field_cols = []
    translated_manual_fields = {"sale_order_line": [], "sale_order_template": []}

    for so_id, ss_id, model in model_ids:
        table = util.table_of_model(cr, model)
        table_sub = table.replace("order", "subscription")
        cr.execute(
            """
            WITH info AS (
               -- get stored fields from subscription table that are not in order table
               SELECT f.id,
                      f.name,
                      c.udt_name
                 FROM ir_model_fields f
            LEFT JOIN information_schema.columns c
                   ON f.name = c.column_name
                  AND c.table_name = %(table_sub)s
            LEFT JOIN ir_model_fields forder
                   ON forder.name = f.name
                  AND forder.model_id = %(so_id)s
                  AND forder.model = %(model)s
                WHERE f.state = 'manual'
                  AND f.model_id = %(ss_id)s
                  AND f.model = %(sub_model)s
                  AND forder.id IS NULL
                  AND (  f.ttype IN ('many2many', 'one2many') -- x2m fields do not have a column
                      OR c.column_name IS NOT NULL
                      )
                )
                -- update the subscription fields that we can move
                UPDATE ir_model_fields f
                   SET model_id = %(so_id)s,
                       model = %(model)s
                  FROM info
                 WHERE f.id = info.id
                 -- return new column name and type
             RETURNING quote_ident(f.name),
                       info.udt_name,
                       f.translate
            """,
            {
                "so_id": so_id,
                "model": model,
                "ss_id": ss_id,
                "sub_model": model.replace("sale.order", "sale.subscription"),
                "table_sub": table_sub,
            },
        )
        info = [r for r in cr.fetchall() if r[1]]  # filter out m2m fields that do not have a column
        if info:
            _logger.info(
                "Create custom field columns in table %s from table %s: %s",
                table,
                table_sub,
                ",".join(r[0] for r in info),
            )
            cr.execute(
                "ALTER TABLE {}\n{}".format(
                    table, ",\n".join(f"ADD COLUMN {col_name} {col_type}" for col_name, col_type, _ in info)
                )
            )
            if table == "sale_order":
                manual_field_cols = [r[0] for r in info]

            if table != "sale_order":
                translated_manual_fields[table].extend(col for (col, _, translate) in info if translate)

    query = """
        INSERT INTO sale_order (old_subscription_id, campaign_id, source_id, medium_id, client_order_ref,
                                name,
                                rating_last_value, message_main_attachment_id, stage_id, analytic_account_id,
                                company_id, partner_id, partner_invoice_id,

                                partner_shipping_id, recurring_monthly,
                                date_order, end_date, pricelist_id, close_reason_id, sale_order_template_id,
                                payment_term_id, note, user_id, team_id, country_id, industry_id,

                                access_token, payment_token_id, kpi_1month_mrr_delta, kpi_1month_mrr_percentage,
                                kpi_3months_mrr_delta, kpi_3months_mrr_percentage, percentage_satisfaction, health,
                                stage_category, to_renew, recurring_live,

                                state,
                                is_subscription, currency_id, create_date, create_uid, write_date, write_uid, recurrence_id,
                                start_date, next_invoice_date
                                %s)
             SELECT ss.id, ss.campaign_id, ss.source_id, ss.medium_id, ss.code,
                    -- match sub display_name
                    coalesce(nullif(concat_ws('/', sst.code, nullif(concat_ws(' - ', ss.code, p.display_name), '')), ''), ss.name),
                    ss.rating_last_value, ss.message_main_attachment_id, ss.stage_id, ss.analytic_account_id,
                    ss.company_id, COALESCE(ss.partner_id, %%(p)s), COALESCE(ss.partner_invoice_id, ss.partner_id, %%(p)s),

                    COALESCE(ss.partner_shipping_id, ss.partner_id, %%(p)s), ss.recurring_monthly,
                    COALESCE(ss.date_start, now() at time zone 'UTC'), ss.date, ss.pricelist_id, ss.close_reason_id, sot.id,
                    ss.payment_term_id, ss.description, ss.user_id, ss.team_id, ss.country_id, ss.industry_id,

                    ss.access_token, ss.payment_token_id, ss.kpi_1month_mrr_delta, ss.kpi_1month_mrr_percentage,
                    ss.kpi_3months_mrr_delta, ss.kpi_3months_mrr_percentage, ss.percentage_satisfaction, ss.health,
                    ss.stage_category, ss.to_renew, (ss.stage_category='progress'),

                    CASE
                        WHEN ss.stage_category='draft' THEN 'sent'
                        ELSE 'sale'
                    END,
                    TRUE, pl.currency_id, ss.create_date, ss.create_uid, ss.write_date, ss.write_uid, str.id,
                    ss.date_start, ss.recurring_next_date
                    %s
               FROM sale_subscription ss
               JOIN sale_order_template sot
                 ON sot.old_template_id = ss.template_id
               JOIN product_pricelist pl
                 ON pl.id = ss.pricelist_id
               JOIN sale_temporal_recurrence str
                 ON ss.template_id = ANY(str._mig_sst_id)
               JOIN sale_subscription_template sst
                 ON sst.id = ss.template_id
          LEFT JOIN res_partner p
                 ON p.id = ss.partner_id
    """
    insert_add = ""
    select_add = ""
    if manual_field_cols:
        insert_add += "," + ",".join(manual_field_cols)
        select_add += "," + ",".join(f"ss.{col}" for col in manual_field_cols)
    # Add the necessary columns and necessary values
    if util.column_exists(cr, "sale_order", "picking_policy"):
        cr.execute(
            """
            SELECT DISTINCT ON (company_id) company_id, id
              FROM stock_warehouse
             ORDER BY company_id, not active, sequence, id
            """
        )
        default_warehouse_id = cr.mogrify(
            "(%s::jsonb->>ss.company_id::text)::int", [Json(dict(cr.fetchall()))]
        ).decode()
        # subscription is only usable for service product
        insert_add += ",picking_policy,warehouse_id"
        select_add += f",'direct',{default_warehouse_id}"
    if util.module_installed(cr, "partner_commission"):
        util.create_column(cr, "sale_order", "commission_plan_frozen", "boolean")
        insert_add += ",referrer_id,commission_plan_frozen,commission_plan_id"
        select_add += ",ss.referrer_id,ss.commission_plan_frozen,ss.commission_plan_id"

    # SO creation
    query = query % (insert_add, select_add)
    cr.execute(query, {"p": util.ref(cr, "base.partner_root")})
    # origin_order_id is the parent order. It points to itself when there is no ancestor (cf commercial_partner_id)
    # Historical subscription have no ancestor at this point
    util.explode_execute(
        cr,
        "UPDATE sale_order SET origin_order_id=id WHERE is_subscription=True AND old_subscription_id IS NOT NULL",
        table="sale_order",
    )

    payment_exception_tag_id = util.ref(cr, "sale_subscription.subscription_invalid_payment")
    if payment_exception_tag_id:
        util.explode_execute(
            cr,
            cr.mogrify(
                """
            UPDATE sale_order so
               SET payment_exception=true
              FROM account_analytic_tag_sale_subscription_rel rel
             WHERE so.old_subscription_id=rel.sale_subscription_id
               AND rel.account_analytic_tag_id=%s
                """,
                [payment_exception_tag_id],
            ).decode(),
            table="sale_order",
            alias="so",
        )
    cr.execute("SELECT id, name FROM sale_subscription_line WHERE product_id IS NULL AND price_unit = 0")
    if cr.rowcount:
        _logger.warning(
            "There are %s subcription lines with no product set and zero unit price, they will be migrated as NOTE order lines:\n * %s",
            cr.rowcount,
            "\n * ".join(f"`{name}` (id={id_})" for id_, name in cr.fetchall()),
        )

    # SO lines creation
    cr.execute(
        """
        INSERT INTO sale_order_line (old_subscription_line_id,old_subscription_id,product_id,product_uom_qty,product_uom,
                                    display_type,
                                    price_unit,discount,price_subtotal,currency_id,order_id,name,
                                    customer_lead,state,
                                    pricing_id,create_date,create_uid,write_date,write_uid,company_id,qty_delivered_method)
        SELECT ssl.id,ssl.analytic_account_id,ssl.product_id,CASE WHEN ssl.product_id IS NULL AND ssl.price_unit = 0 THEN 0 ELSE ssl.quantity END,ssl.uom_id,
               CASE WHEN ssl.product_id IS NULL AND ssl.price_unit = 0 THEN 'line_note' else NULL END,
               ssl.price_unit,ssl.discount,ssl.price_subtotal,ssl.currency_id,so.id,ssl.name,
               0,so.state,ppr.id,ssl.create_date,ssl.create_uid,ssl.write_date,ssl.write_uid,so.company_id,'manual'

          FROM sale_subscription_line ssl
          JOIN sale_subscription ss ON ss.id=ssl.analytic_account_id
          JOIN sale_order so ON so.old_subscription_id=ss.id
          JOIN sale_subscription_template sst ON ss.template_id=sst.id
          LEFT JOIN product_pricing ppr ON ssl.id = ANY (ppr._mig_sub_line_id)
        """
    )
    util.remove_column(cr, "product_pricing", "_mig_sub_line_id")

    # Recreate M2M table
    cr.execute(
        """
        CREATE TABLE sale_order_template_tag_rel (
            template_id INTEGER,
            tag_id INTEGER,
            PRIMARY KEY (template_id, tag_id)
        )
        """
    )
    cr.execute(
        """
        INSERT INTO sale_order_template_tag_rel (template_id,tag_id)
        SELECT old_tag_rel.template_id,old_tag_rel.tag_id
          FROM sale_subscription_template_tag_rel old_tag_rel
        """
    )
    cr.execute(
        """
        CREATE TABLE sale_order_starred_user_rel (
            order_id INTEGER,
            user_id INTEGER,
            PRIMARY KEY (order_id, user_id)
        )
        """
    )
    cr.execute(
        """
        INSERT INTO sale_order_starred_user_rel (order_id,user_id)
        SELECT so.id,old_star_rel.user_id
          FROM  subscription_starred_user_rel old_star_rel
          JOIN sale_order so ON so.old_subscription_id=old_star_rel.subscription_id
        """
    )
    # Update the logs
    util.parallel_execute(
        cr,
        util.explode_query_range(
            cr,
            """
        UPDATE sale_order_log ssl
           SET order_id=so.id
          FROM sale_order so
         WHERE so.old_subscription_id=ssl.old_subscription_id
            """,
            alias="ssl",
            table="sale_order_log",
        ),
    )
    # Update the account move line subscription_id
    cr.execute("ALTER TABLE account_move_line RENAME COLUMN subscription_id TO old_subscription_id")
    cr.execute("CREATE INDEX ON account_move_line (old_subscription_id) WHERE old_subscription_id IS NOT NULL")

    util.create_column(cr, "account_move_line", "subscription_id", "int4")
    cr.execute("CREATE INDEX ON account_move_line (subscription_id) WHERE subscription_id IS NOT NULL")
    util.parallel_execute(
        cr,
        util.explode_query_range(
            cr,
            """
        UPDATE account_move_line aml
           SET subscription_id=so.id
          FROM sale_order so
         WHERE so.old_subscription_id=aml.old_subscription_id
            """,
            alias="aml",
            table="account_move_line",
        ),
    )

    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("sale_subscription.{subscription_invalid_payment,invoice_batch}"))
    # rename models
    util.rename_model(cr, "sale.subscription.close.reason", "sale.order.close.reason")
    util.rename_model(cr, "sale.subscription.alert", "sale.order.alert")
    util.rename_model(cr, "sale.subscription.stage", "sale.order.stage")

    # Remove unneeded models and fields
    util.remove_field(cr, "sale.subscription.report", "date_end")
    util.remove_field(cr, "sale.subscription.report", "date_start")
    util.remove_field(cr, "product.product", "subscription_template_id", drop_column=False)
    util.remove_field(cr, "product.template", "subscription_template_id", drop_column=False)
    # let the transient models be recreated
    util.remove_model(cr, "sale.subscription.renew.wizard")
    util.remove_model(cr, "sale.subscription.renew.wizard.replace_option")
    util.remove_model(cr, "sale.subscription.renew.wizard.keep_option")
    util.remove_model(cr, "sale.subscription.renew.wizard")
    util.remove_model(cr, "sale.subscription.wizard.option")
    util.remove_model(cr, "sale.subscription.wizard")

    # Merge all references
    cr.execute(
        """
        SELECT old_subscription_id,id
          FROM sale_order
         WHERE old_subscription_id IS NOT NULL
        """
    )
    if cr.rowcount:
        util.replace_record_references_batch(cr, dict(cr.fetchall()), "sale.subscription", "sale.order")

    cr.execute(
        """
        SELECT old_template_id,id
          FROM sale_order_template
         WHERE old_template_id IS NOT NULL
        """
    )
    util.replace_record_references_batch(cr, dict(cr.fetchall()), "sale.subscription.template", "sale.order.template")

    already_processed_fk = [
        ("sale_order", "old_subscription_id"),
        ("sale_order_line", "old_subscription_line_id"),
        ("sale_subscription_line", "analytic_account_id"),
        ("account_move_line", "old_subscription_id"),
    ]
    util.create_column(cr, "sale_subscription", "new_sale_order_id", "int4")
    util.create_column(cr, "sale_subscription_line", "new_sale_order_line_id", "int4")
    util.create_column(cr, "sale_subscription_template", "new_sale_order_template_id", "int4")
    util.parallel_execute(
        cr,
        [
            """
        UPDATE sale_subscription ss
           SET new_sale_order_id=so.id
          FROM sale_order so
         WHERE so.old_subscription_id=ss.id
            """,
            """
        UPDATE sale_subscription_line ssl
           SET new_sale_order_line_id=sol.id
          FROM sale_order_line sol
         WHERE sol.old_subscription_line_id=ssl.id
            """,
            """
        UPDATE sale_subscription_template sst
           SET new_sale_order_template_id=sot.id
          FROM sale_order_template sot
         WHERE sot.old_template_id=sst.id
            """,
        ],
    )
    cr.execute("CREATE INDEX ON sale_subscription(new_sale_order_id)")
    cr.execute("CREATE INDEX ON sale_subscription_line(new_sale_order_line_id)")

    sale_order_line_translations = {
        f"sale.subscription.line,{field}": f"sale.order.line,{field}"
        for field in translated_manual_fields["sale_order_line"]
    }
    if sale_order_line_translations:
        queries = [
            cr.mogrify(query, [Json(sale_order_line_translations), tuple(sale_order_line_translations)])
            for query in util.explode_query_range(
                cr,
                """
                UPDATE ir_translation it
                   SET name = %s::jsonb->>it.name,
                       res_id = ssl.new_sale_order_line_id
                  FROM sale_subscription_line ssl
                 WHERE it.name IN %s
                   AND ssl.id = it.res_id
                """,
                table="ir_translation",
                alias="it",
            )
        ]

        util.parallel_execute(cr, queries)

    sale_order_template_translations = {
        f"sale.subscription.template,{field}": f"sale.order.template,{field}"
        for field in translated_manual_fields["sale_order_template"]
    }
    if sale_order_template_translations:
        queries = [
            cr.mogrify(query, [Json(sale_order_template_translations), tuple(sale_order_template_translations)])
            for query in util.explode_query_range(
                cr,
                """
                UPDATE ir_translation it
                   SET name = %s::jsonb->>it.name,
                       res_id = sst.new_sale_order_template_id
                  FROM sale_subscription_template sst
                 WHERE it.name IN %s
                   AND sst.id = it.res_id
                """,
                table="ir_translation",
                alias="it",
            )
        ]

        util.parallel_execute(cr, queries)

    for main_table, map_field in [
        ("sale_subscription", "new_sale_order_id"),
        ("sale_subscription_line", "new_sale_order_line_id"),
        ("sale_subscription_template", "new_sale_order_template_id"),
    ]:
        for table, column, conname, _ in util.get_fk(cr, main_table, quote_ident=False):
            if (table, column) not in already_processed_fk:
                _logger.info("Switch foreign key from %s.%s for %s", table, column, main_table)
                cr.execute(f'ALTER TABLE "{table}" DROP CONSTRAINT "{conname}"')
                if util.column_exists(cr, table, "id"):
                    util.parallel_execute(
                        cr,
                        util.explode_query_range(
                            cr,
                            f"""
                                UPDATE "{table}" t
                                SET "{column}"=m.{map_field}
                                FROM "{main_table}" m
                                WHERE t."{column}"=m.id
                            """,
                            alias="t",
                            table=table,
                        ),
                    )
                else:
                    # {table} is an m2m, recreate it with the right data
                    (column2,) = util.get_columns(cr, table, ignore=(column,))  # will fail if not m2m
                    table2 = util.target_of(cr, table, column2)[0]
                    cr.execute(f'ALTER TABLE "{table}" RENAME TO "{table}_upg"')
                    new_table = main_table.replace("subscription", "order")
                    if table2 == main_table:
                        # m2m to itself from the model of main_table
                        util.create_m2m(cr, table, new_table, new_table, col1=column, col2=column2)
                        query = f"""
                        INSERT INTO "{table}" ("{column2}", {column})
                             SELECT m2.{map_field}, m.{map_field}
                               FROM "{table}_upg" orig_t
                               JOIN "{main_table}" m
                                 ON orig_t."{column}"=m.id
                               JOIN "{main_table}" m2
                                 ON orig_t."{column2}"=m2.id
                        """
                        already_processed_fk.append((table, column2))
                    else:
                        util.create_m2m(cr, table, new_table, table2, col1=column, col2=column2)
                        query = f"""
                        INSERT INTO "{table}" ("{column2}", {column})
                             SELECT orig_t."{column2}", m.{map_field}
                               FROM "{table}_upg" orig_t
                               JOIN "{main_table}" m
                                 ON orig_t."{column}"=m.id
                        """
                    # Do not exec in // or face the issue where a record is updated/converted multiple times
                    # We cannot just update the m2m table because there may be conflicts
                    cr.execute(query)
                    cr.execute(f'DROP TABLE "{table}_upg"')

    # Update sale_order_line_invoice_rel to match the new sale orders
    cr.execute(
        """
        WITH amls AS (
            SELECT id,
                subscription_id,
                product_id,
                row_number() OVER (PARTITION BY subscription_id, product_id, move_id ORDER BY move_id, id) as nr
            FROM account_move_line
        ),
        sols AS (
            SELECT id,
                order_id,
                product_id,
                row_number() OVER (PARTITION BY order_id, product_id ORDER BY id) as nr
            FROM sale_order_line
        )
        INSERT INTO sale_order_line_invoice_rel(invoice_line_id,order_line_id)
             SELECT amls.id,sols.id
               FROM amls
               JOIN sols ON amls.subscription_id=sols.order_id
                        AND amls.product_id=sols.product_id
                        AND amls.nr=sols.nr
        ON CONFLICT DO NOTHING
        """
    )
    # Define the origin (ancestor) and subscription_id (parent) on subscription. It allows to keep the link between subscription
    # and the sale orders (renew, upsell and creator).
    # Note: there is a limitation. In the old system, a sale order could create several subscription with different templates
    # (periodicity) when they were confirmed. The SOL was linked to the subscription with the subscription_id field.
    # In the new system, one sale order can only have one parent. If a sale order created multiple subscription, only one is kept
    # The information is still available in the chatter but The link to the parent is lost.
    util.parallel_execute(
        cr,
        util.explode_query_range(
            cr,
            """
            UPDATE sale_order so
               SET origin_order_id=sol.subscription_id,
                   subscription_id=sol.subscription_id
              FROM sale_order_line sol
             WHERE so.id=sol.order_id
               AND sol.subscription_id IS NOT NULL
            """,
            alias="so",
            table="sale_order",
        ),
    )
    # We convert renew orders to adapt to the new flow.
    # quotations are subscription, they will generate several invoices
    # confirmed sale orders are not subscription. They already generated their unique invoice. We move them in a closed category
    # with a custom subscription_management value
    # Pricing will be updated and salesmen will need to check them.
    # We must not modify further confirmed renew quotation because they already updated the parent subscription that was converted
    # above. In all cases, these quotations must be reviewed. Setting is_subscription allows to keep the record and his history.
    stages = {}
    for st, vals in [
        ("draft", ["Quotation", 10, "draft", False]),
        ("closed", ["Closed", 40, "closed", True]),
    ]:
        # Ensure that both the reference and the record exist, take into account the rename sale.{subscription->order}.stage
        stages[st] = util.ref(cr, f"sale_subscription.sale_subscription_stage_{st}")
        if stages[st] is None:
            cr.execute(
                """
                WITH new_rec AS (
                    INSERT INTO sale_order_stage (name, sequence, category, fold)
                         VALUES (%s, %s, %s, %s)
                      RETURNING id
                )
                INSERT INTO ir_model_data (module, name, model, res_id, noupdate)
                     SELECT 'sale_subscription', 'sale_subscription_stage_'||%s, 'sale.order.stage', new_rec.id, True
                       FROM new_rec
                ON CONFLICT (module, name)
                  DO UPDATE SET res_id = EXCLUDED.res_id
                """,
                [*vals, st],
            )
            stages[st] = util.ref(cr, f"sale_subscription.sale_subscription_stage_{st}")

    query = cr.mogrify(
        """
        UPDATE sale_order so
           SET is_subscription= CASE
               WHEN so.state IN ('draft', 'sent') THEN true
               ELSE false
           END,
           subscription_management= CASE
               WHEN so.state IN ('sale', 'done') THEN 'renewal_so'
               ELSE so.subscription_management
           END,
           recurrence_id=parent_sub.recurrence_id,
           next_invoice_date=
           CASE
               WHEN so.state IN ('sale', 'done') THEN current_date
               ELSE NULL
           END,
           stage_category=
           CASE
               WHEN so.state IN ('draft', 'sent') THEN 'draft'
               WHEN so.state IN ('sale', 'done') THEN 'closed'
           END,
           stage_id=
           CASE
               WHEN so.state IN ('draft', 'sent') THEN %(draft)s
               WHEN so.state IN ('sale', 'done') THEN %(closed)s
           END
          FROM sale_order parent_sub
         WHERE parent_sub.id=so.subscription_id
           AND so.subscription_management='renew'
        """,
        stages,
    ).decode()
    util.parallel_execute(
        cr,
        util.explode_query_range(
            cr,
            query,
            table="sale_order",
            alias="so",
        ),
    )

    # Set the recurrence_id when subscription_management is `create`
    util.explode_execute(
        cr,
        """
        UPDATE sale_order AS so
           SET recurrence_id = parent_sub.recurrence_id
          FROM sale_order AS parent_sub
         WHERE so.subscription_id = parent_sub.id
           AND so.subscription_management = 'create'
           AND so.recurrence_id IS NULL
           AND parent_sub.recurrence_id IS NOT NULL
        """,
        table="sale_order",
        alias="so",
    )

    util.parallel_execute(
        cr,
        util.explode_query_range(
            cr,
            """
            UPDATE sale_order so
               SET stage_category=sc.category
              FROM sale_order_stage sc
             WHERE sc.id=so.stage_id
            """,
            alias="so",
            table="sale_order",
        ),
    )
    # Update the draft upsell and renew to adapt them to the new system.
    # The business code needs a link between the upsell/renew lines and the line in the parent
    # subscription with same product_id, uom, price_unit. This link is only needed at SO confirmation.
    # The new system take care of this link at the quotation creation but we need to handle existing draft quotations.
    # The link is called parent_line_id. The pricing, start_date and next_invoice_date are set according to the values of the parent
    # line.
    # This link is handled with the following condition:
    # `join JOIN sale_order_line sol ON sol.subscription_id=sol_sub.order_id`
    # sol is the sale_order_line of the child renew/upsell because the former system kept a link between the sale_order_line and the
    # sale.subscription with the subscription_id field on the sale_order_line.
    # Thanks to the above FK upgrade, the sol.subscription_id is now updated to the new sale_order id value (parent subscription)
    # It is therefore correct to retrieve the sol parent subscription id by using the subscription_id value
    cr.execute(
        """
               SELECT sol_sub.id,
                      sol_sub.pricing_id,
                      sol_sub.product_id,
                      sol_sub.product_uom,
                      sol_sub.price_unit,
                      sol_sub.order_id,
                      CASE so.subscription_management
                         WHEN 'upsell' THEN CURRENT_DATE::timestamp
                         ELSE so.next_invoice_date
                      END as start_date
        INTO UNLOGGED _upgrade_tmp_sol2
                 FROM sale_order_line sol_sub
                 JOIN sale_order_line sol ON sol.subscription_id=sol_sub.order_id
                 JOIN sale_order so ON so.id=sol.order_id
                WHERE so.subscription_management IN ('upsell', 'renew')
                  AND so.state='draft';
         CREATE INDEX _upgrade_tmp_sol2_idx
                   ON _upgrade_tmp_sol2 (product_id, product_uom, price_unit, order_id)
        """
    )
    util.explode_execute(
        cr,
        """
        UPDATE sale_order_line sol_update
           SET parent_line_id=sol2.id,
               pricing_id=COALESCE(sol2.pricing_id, sol_update.pricing_id)
          FROM _upgrade_tmp_sol2 sol2
         WHERE sol2.product_id=sol_update.product_id
           AND sol2.product_uom=sol_update.product_uom
           AND sol2.price_unit=sol_update.price_unit
           AND sol_update.subscription_id=sol2.order_id
           AND {parallel_filter}
        """,
        table="sale_order_line",
        alias="sol_update",
    )
    cr.execute("DROP TABLE _upgrade_tmp_sol2")

    # Set stage_id for draft quotations that have recurring products, ie quotations that
    # are yet to become subscriptions (once confirmed post-upgrade).
    query = cr.mogrify(
        """
        UPDATE sale_order so
           SET stage_id = %(draft)s
          FROM sale_order_line sol
          JOIN product_product pp ON pp.id = sol.product_id
          JOIN product_template pt ON  pt.id = pp.product_tmpl_id
         WHERE sol.order_id = so.id
           AND pt.recurring_invoice = True
           AND so.subscription_management = 'create'
           AND so.state IN ('draft', 'sent')
           AND so.stage_id IS NULL
        """,
        stages,
    ).decode()
    util.explode_execute(
        cr,
        query,
        table="sale_order",
        alias="so",
    )

    # In the old system, the client_order_ref was not copied from the subscription to the upsell/renewal
    util.explode_execute(
        cr,
        """
        UPDATE sale_order so
           SET client_order_ref=sub.code
          FROM sale_subscription sub
         WHERE sub.new_sale_order_id=so.subscription_id
           AND so.client_order_ref IS NULL
        """,
        table="sale_order",
        alias="so",
    )

    util.remove_field(cr, "sale.order.line", "subscription_id")

    if util.table_exists(cr, "account_analytic_tag_sale_order_rel"):
        util.create_column(cr, "account_analytic_tag_sale_order_rel", "account_analytic_tag_sale_order_rel", "int4")
    _logger.info("Merge model sale.subscription into sale.order")
    util.merge_model(cr, "sale.subscription", "sale.order", drop_table=False)
    _logger.info("Merged model sale.subscription into sale.order")

    util.update_field_usage(cr, "sale.order", "template_id", "sale_order_template_id")
    util.update_field_usage(cr, "sale.order", "recurring_invoice_line_ids", "order_line")

    util.remove_view(cr, "sale_subscription.view_sale_subscription_order_line")
    util.remove_view(cr, "sale_subscription.wizard_form_view")

    util.create_column(cr, "sale_order_option", "option_pricing_id", "int4")
    util.create_column(cr, "sale_order_template", "color", "int4")
    util.create_column(cr, "sale_order_template_line", "pricing_id", "int4")
    util.create_column(cr, "sale_order_template_option", "option_pricing_id", "int4")

    util.force_noupdate(cr, "sale_subscription.sale_subscription_stage_draft", noupdate=True)
    util.force_noupdate(cr, "sale_subscription.sale_subscription_stage_in_progress", noupdate=True)
    util.force_noupdate(cr, "sale_subscription.sale_subscription_stage_closed", noupdate=True)
    cr.commit()

    if util.column_exists(cr, "account_analytic_line", "order_id"):
        cr.execute("create index account_analytic_line_order_id_idx on account_analytic_line using btree(order_id)")
    cr.execute("create index sale_order_subscription_id_idx on sale_order using btree(subscription_id)")
    cr.execute("create index sale_order_origin_order_id_idx on sale_order using btree(origin_order_id)")
    cr.execute("create index sale_order_line_parent_line_id_idx on sale_order_line using btree(parent_line_id)")
    util.remove_model(cr, "sale.subscription.template", drop_table=False)

    restore_manual_fields_models = [
        (
            util.ref(cr, "sale.model_sale_order_line"),
            "new_sale_order_line_id",
            "sale_order_line",
            "sale_subscription_line",
        ),
        (
            util.ref(cr, "sale_management.model_sale_order_template"),
            "new_sale_order_template_id",
            "sale_order_template",
            "sale_subscription_template",
        ),
    ]

    for model_id, field, table, table_sub in restore_manual_fields_models:
        cr.execute(
            """
            SELECT f.name
              FROM ir_model_fields f
              JOIN information_schema.columns c1
                ON f.name = c1.column_name
               AND c1.table_name = %s
              JOIN information_schema.columns c2
                ON f.name = c2.column_name
               AND c2.table_name = %s
             WHERE f.model_id = %s
               AND f.state = 'manual'
               AND f.store = True
               AND f.ttype != 'binary'
            """,
            [table, table_sub, model_id],
        )
        info = cr.fetchall()
        columns = ",".join([f'"{column}" = {table_sub}."{column}"' for (column,) in info])
        if columns:
            query = f"""
                    UPDATE {table} t
                       SET {columns}
                      FROM {table_sub}
                     WHERE {table_sub}.{field} = t.id
                    """
            util.explode_execute(cr, query, table=table, alias="t")


def _handle_recurring_renting_products(cr):
    """
    Before 15.3, a product_template could be recurring and used in rental sale order
    It is not possible anymore because the temporal_type of a line is a selection field: rental/subscription.
    In this function, the product with both rental and recurring_invoice attributes set to true are
    duplicated when they are used in sale_subscription_line. If they had both attributes but were not used in subscription,
    the recurring_invoice attribute is simply set to false. We avoid duplicating records for nothing.
    """
    cr.execute(
        """
          SELECT pp.id,product_tmpl_id
            FROM product_product pp
            JOIN product_template pt ON pt.id=pp.product_tmpl_id
           WHERE pt.recurring_invoice=true
             AND pt.rent_ok = true
        """
    )
    product_results = cr.dictfetchall()
    pp_ids = [val["id"] for val in product_results]
    if pp_ids:
        cr.execute(
            """
            SELECT product_id
            FROM sale_subscription_line ssl
            WHERE ssl.product_id IN %s
            """,
            [tuple(pp_ids)],
        )
        used_product = cr.fetchall()
        used_product = [v[0] for v in used_product]
    else:
        used_product = []
    # We just mark the product not appearing in subscription as not recurring. User will have to duplicate it
    # manually if they want to use them in subscription
    non_used_subscription_templates = [
        val["product_tmpl_id"] for val in product_results if val["id"] not in used_product
    ]
    if non_used_subscription_templates:
        cr.execute(
            """
            UPDATE product_template
            SET recurring_invoice=false
            WHERE id IN %s
            """,
            [tuple(non_used_subscription_templates)],
        )
    # We need to duplicate the products used in subscription to prevent issues.
    used_templates = {val["product_tmpl_id"] for val in product_results if val["id"] in used_product}
    if used_templates:
        # We duplicate the product variant with the orm to handle variants, attribute values, attribute line constraints.
        # This is a niche case that should not happen a lot.
        env = util.env(cr)
        existing_product_ids = env["product.product"].browse(set(used_product))
        template_mapping = {}
        case_str = ""
        archived_products = []
        for product in existing_product_ids:
            if product.product_tmpl_id.product_variant_count > 1:
                # We archive the product to avoid using it again in the future
                product.active = False
                archived_products.append(product.display_name)
                continue
            # We need to duplicate the variant in the loop. copy_data don't work.
            # /!\ inefficient but we hope to have less than a few hundred product
            new_product = product.copy()
            new_product.product_tmpl_id.product_pricing_ids = [(5, 0, 0)]
            template_mapping[product.product_tmpl_id.id] = new_product.product_tmpl_id.id
            case_str += cr.mogrify("WHEN product_id=%s THEN %s\n", [product.id, new_product.id]).decode()

        if case_str:
            cr.execute(
                f"""
                UPDATE sale_subscription_line
                   SET product_id = CASE
                           {case_str}
                           ELSE product_id
                       END
                """
            )

            cr.execute(
                """
                UPDATE product_template
                   SET recurring_invoice=true,rent_ok=false
                 WHERE id IN %s
                """,
                [tuple(template_mapping.values())],
            )

        cr.execute(
            """
            UPDATE product_template
               SET recurring_invoice=false,rent_ok=true
             WHERE id IN %s
            """,
            [tuple(used_templates)],
        )

        if archived_products:
            # TODO html formatting of the output
            util.add_to_migration_reports(
                "Several products were configured to be rented and used in subscription. This use case is not supported anymore. "
                "We converted the products with only one variant but some product had multiple variants and were used in both"
                "Subscriptions and Rental orders. We archived it to prevent issues in the future. You need to duplicate"
                "products template that need to be both used in subscription and rental and update the draft and confirmed "
                "subscription with the relevant product copy.\n"
                "The archived products are {}".format(", ".join(archived_products))
            )


# During the migration, sale_subscription is in init mode, thanks to sale_temporal
# This leads to a write on stage category, and then a recompute on all subscriptions.
# -> Memory Error :D
class Stage(models.Model):
    _inherit = "sale.order.stage"
    _module = "sale_subscription"

    def write(self, vals):
        if "category" in vals:
            vals.pop("category")
        return super().write(vals)
