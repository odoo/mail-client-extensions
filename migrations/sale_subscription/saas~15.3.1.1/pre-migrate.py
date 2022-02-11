# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "sale.order", "subscription_count")
    util.remove_view(cr, "sale_subscription.sale_subscription_order_form_view")
    util.create_column(cr, "sale_order_template", "recurring_rule_type", "varchar")
    util.create_column(cr, "sale_order_template", "recurring_rule_boundary", "varchar")
    util.create_column(cr, "sale_order_template", "recurring_rule_count", "int4")
    util.create_column(cr, "sale_order_template", "user_closable", "boolean")
    util.create_column(cr, "sale_order_template", "payment_mode", "varchar")
    util.create_column(cr, "sale_order_template", "auto_close_limit", "int4")
    util.create_column(cr, "sale_order_template", "good_health_domain", "varchar")
    util.create_column(cr, "sale_order_template", "bad_health_domain", "varchar")
    util.create_column(cr, "sale_order_template", "invoice_mail_template_id", "int4")
    # temporary column used to retrieve the tags
    util.create_column(cr, "sale_order_template", "old_template_id", "int4")
    cr.execute(
        """
        INSERT INTO sale_order_template (old_template_id,name,active,note,recurring_rule_type,
                                         recurring_rule_boundary,recurring_rule_count,user_closable,payment_mode,auto_close_limit,
                                         good_health_domain,bad_health_domain,invoice_mail_template_id,company_id)
             SELECT id,CONCAT ('Migrated ', name),active,description,recurring_rule_type,
                    recurring_rule_boundary,recurring_rule_count,user_closable,payment_mode,auto_close_limit,
                    good_health_domain,bad_health_domain,invoice_mail_template_id,company_id
               FROM sale_subscription_template
        """
    )

    util.create_column(cr, "sale_order", "old_subscription_id", "int4")
    util.create_column(cr, "sale_order", "is_subscription", "boolean")
    util.create_column(cr, "sale_order", "to_renew", "boolean")
    util.create_column(cr, "sale_order", "payment_exception", "boolean")
    util.create_column(cr, "sale_order", "rating_last_value", "float8")
    util.create_column(cr, "sale_order", "stage_id", "int4")
    util.create_column(cr, "sale_order", "end_date", "date")
    util.create_column(cr, "sale_order", "close_reason_id", "int4")
    util.create_column(cr, "sale_order", "country_id", "int4")
    util.create_column(cr, "sale_order", "industry_id", "int4")
    util.create_column(cr, "sale_order", "payment_token_id", "int4")
    util.create_column(cr, "sale_order", "kpi_1month_mrr_delta", "float8")
    util.create_column(cr, "sale_order", "kpi_1month_mrr_percentage", "float8")
    util.create_column(cr, "sale_order", "kpi_3months_mrr_delta", "float8")
    util.create_column(cr, "sale_order", "kpi_3months_mrr_percentage", "float8")
    util.create_column(cr, "sale_order", "percentage_satisfaction", "int4")
    util.create_column(cr, "sale_order", "health", "varchar")
    util.create_column(cr, "sale_order", "stage_category", "varchar")
    util.create_column(cr, "sale_order", "origin_order_id", "int4")

    util.create_column(cr, "sale_order_line", "old_subscription_line_id", "int4")
    util.create_column(cr, "sale_order_line", "old_subscription_id", "int4")

    util.rename_model(cr, "sale.subscription.log", "sale.order.log")
    util.rename_field(cr, "sale.order.log", "subscription_id", "order_id")
    cr.execute("ALTER TABLE sale_order_log RENAME COLUMN order_id TO old_subscription_id")
    util.create_column(cr, "sale_order_log", "order_id", "int4")

    # Rename rule type of template to ease the migration
    util.change_field_selection_values(
        cr,
        "sale.subscription.template",
        "recurring_rule_type",
        {"daily": "day", "weekly": "week", "monthly": "month", "yearly": "year"},
    )
    # pricing creation
    cr.execute(
        """
        INSERT INTO product_pricing (price,duration,product_template_id,currency_id,unit)
        SELECT DISTINCT ssl.price_unit AS price,sst.recurring_interval AS duration,
               pp.product_tmpl_id AS product_template_id,ssl.currency_id,sst.recurring_rule_type
          FROM sale_subscription_line ssl
          JOIN product_product pp ON ssl.product_id=pp.id
          JOIN sale_subscription ss on ss.id=ssl.analytic_account_id
          JOIN sale_subscription_template sst ON ss.template_id=sst.id
        """
    )
    query = """
        INSERT INTO sale_order (old_subscription_id,name,campaign_id,source_id,medium_id,client_order_ref,
                                rating_last_value,message_main_attachment_id,stage_id,analytic_account_id,
                                company_id,partner_id,partner_invoice_id,partner_shipping_id,
                                date_order,end_date,pricelist_id,close_reason_id,sale_order_template_id,payment_term_id,
                                note,user_id,team_id,country_id,industry_id,
                                access_token,payment_token_id,kpi_1month_mrr_delta,kpi_1month_mrr_percentage,kpi_3months_mrr_delta,
                                kpi_3months_mrr_percentage,percentage_satisfaction,health,stage_category,to_renew,
                                is_subscription,currency_id %s)
             SELECT ss.id,ss.name,campaign_id,source_id,medium_id,ss.code,
                    rating_last_value,message_main_attachment_id,stage_id,analytic_account_id,
                    ss.company_id,partner_id,COALESCE(partner_invoice_id, partner_id),COALESCE(partner_shipping_id, partner_id),
                    date_start,date,pricelist_id,close_reason_id,template_id,payment_term_id,
                    description,user_id,team_id,country_id,industry_id,
                    access_token,payment_token_id,kpi_1month_mrr_delta,kpi_1month_mrr_percentage,kpi_3months_mrr_delta,
                    kpi_3months_mrr_percentage,percentage_satisfaction,health,stage_category,to_renew,
                    TRUE,pl.currency_id %s
               FROM sale_subscription ss
               JOIN product_pricelist pl ON pl.id=ss.pricelist_id
    """
    insert_add = ""
    select_add = ""
    # Add the necessary columns and necessary values
    if util.module_installed(cr, "sale_stock"):
        env = util.env(cr)
        default_warehouse_id = env["stock.warehouse"].search([], limit=1).id
        # subscription is only usable for service product
        insert_add += ",picking_policy,warehouse_id"
        select_add += f",'direct',{default_warehouse_id}"
    if util.module_installed(cr, "partner_commission"):
        util.create_column(cr, "sale_order", "commission_plan_frozen", "boolean")
        insert_add += ",referrer_id,commission_plan_frozen,commission_plan_id"
        select_add += ",referrer_id,commission_plan_frozen,commission_plan_id"
    # SO creation
    query = query % (insert_add, select_add)
    cr.execute(query)
    # origin_order_id is the parent order. It points to itself when there is no ancestor (cf commercial_partner_id)
    # Historical subscription have no ancestor at this point
    cr.execute("UPDATE sale_order SET origin_order_id=id WHERE is_subscription=True")
    payment_exception_tag_id = util.ref(cr, "sale_subscription.subscription_invalid_payment")
    if payment_exception_tag_id:
        cr.execute(
            """
            UPDATE sale_order so
               SET payment_exception=true
              FROM account_analytic_tag_sale_subscription_rel rel
             WHERE so.old_subscription_id=rel.sale_subscription_id
              AND account_analytic_tag_id=%s
            """,
            [payment_exception_tag_id],
        )
    # SO lines creation
    cr.execute(
        """
        INSERT INTO sale_order_line (old_subscription_line_id,old_subscription_id,product_id,product_uom_qty,product_uom,
                                    price_unit,discount,price_subtotal,currency_id,order_id,name,
                                    start_date,next_invoice_date,customer_lead,
                                    pricing_id)
        SELECT ssl.id,ssl.analytic_account_id,ssl.product_id,ssl.quantity,ssl.uom_id,
               ssl.price_unit,ssl.discount,ssl.price_subtotal,ssl.currency_id,so.id,ssl.name,
               ss.date_start,ss.recurring_next_date,0,ppr.id

          FROM sale_subscription_line ssl
          JOIN sale_subscription ss ON ss.id=ssl.analytic_account_id
          JOIN sale_order so ON so.old_subscription_id=ss.id
          JOIN sale_subscription_template sst ON ss.template_id=sst.id
          JOIN product_pricing ppr ON ppr.duration=sst.recurring_interval
                                  AND sst.recurring_rule_type=ppr.unit
        """
    )
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
    cr.execute(
        """
        UPDATE sale_order_log ssl
           SET order_id=so.id
          FROM sale_order so
         WHERE so.old_subscription_id=ssl.old_subscription_id
        """
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
    util.remove_field(cr, "product.product", "subscription_template_id")
    util.remove_field(cr, "product.template", "subscription_template_id")
    util.remove_field(cr, "sale.order.line", "subscription_id")
    # let the transient models be recreated
    util.remove_model(cr, "sale.subscription.renew.wizard")
    util.remove_model(cr, "sale.subscription.renew.wizard.replace_option")
    util.remove_model(cr, "sale.subscription.renew.wizard.keep_option")
    util.remove_model(cr, "sale.subscription.renew.wizard")
    util.remove_model(cr, "sale.subscription.wizard.option")
    util.remove_model(cr, "sale.subscription.wizard")
    util.remove_model(cr, "sale.subscription.line")
    # Merge all references
    cr.execute(
        """
        SELECT old_subscription_id,id
          FROM sale_order
         WHERE old_subscription_id IS NOT NULL
        """
    )
    result = cr.fetchall()
    id_mapping = {v[0]: v[1] for v in result}
    if id_mapping:
        util.replace_record_references_batch(cr, id_mapping, "sale.subscription", "sale.order")

    util.merge_model(cr, "sale.subscription", "sale.order", drop_table=False)
    util.remove_model(cr, "sale.subscription.template")

    util.remove_view(cr, "sale_subscription.view_sale_subscription_order_line")
    util.remove_view(cr, "sale_subscription.wizard_form_view")
