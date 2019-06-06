# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def model_id(cr, model):
    cr.execute("SELECT id FROM ir_model WHERE model = %s", [model])
    return cr.fetchone()[0]

def migrate(cr, version):
    # Locations
    cr.execute(
        """
        CREATE TABLE lunch_location (
            id SERIAL NOT NULL PRIMARY KEY,
            name varchar,
            address text
        )
    """
    )
    util.create_m2m(cr, "lunch_alert_lunch_location_rel", "lunch_alert", "lunch_location")
    cr.execute(
        """
        INSERT INTO lunch_location(name, address)
             SELECT name, partner_id::text
               FROM res_company
              WHERE id IN (SELECT company_id FROM lunch_order)
    """
    )
    cr.execute(
        """
        INSERT INTO lunch_alert_lunch_location_rel(lunch_alert_id, lunch_location_id)
             SELECT a.id, l.id
               FROM lunch_alert a
               JOIN lunch_location l ON a.partner_id = l.address::int4
    """
    )
    cr.execute("UPDATE lunch_location SET address = NULL")

    # Alerts
    days = {"monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"}
    cr.execute(
        """
        UPDATE lunch_alert
           SET {}
         WHERE alert_type = 'days'
    """.format(
            ", ".join(d + "=true" for d in days)
        )
    )
    for day in days:
        util.rename_field(cr, "lunch.alert", day, "recurrency_" + day)

    util.rename_field(cr, "lunch.alert", "specific_day", "until")

    for gone in "display alert_type partner_id start_hour end_hour".split():
        util.remove_field(cr, "lunch.alert", gone)

    # Cash Moves
    cr.execute("""
    WITH cashm as (
        SELECT user_id,sum(amount) as cm
          FROM lunch_cashmove
         WHERE state != 'payment'
      GROUP BY user_id),
         o as (
        SELECT sum(price)*(-1) as order,user_id
          FROM lunch_order_line
         WHERE state='confirmed'
      GROUP BY user_id)

    INSERT INTO lunch_cashmove(amount, user_id, description, state, date)
    SELECT amount_diff,user_id,'Mig V12.2','payment',CURRENT_DATE
    FROM (
        SELECT round((coalesce(cashm.cm,0.0)-coalesce(o.order,0.0))::NUMERIC,2) as amount_diff,cashm.user_id
          FROM cashm FULL OUTER JOIN o ON cashm.user_id=o.user_id) as res
    WHERE amount_diff!=0
    """)

    cr.execute("DELETE FROM lunch_cashmove WHERE state != 'payment'")
    util.create_column(cr, "lunch_cashmove", "currency_id", "int4")
    cr.execute(
        """
        UPDATE lunch_cashmove m
           SET currency_id = o.currency_id
          FROM lunch_order_line l
          JOIN lunch_order o ON (o.id = l.order_id)
         WHERE l.id = m.order_id
    """
    )
    util.remove_field(cr, "lunch.cashmove", "order_id")
    util.remove_field(cr, "lunch.cashmove", "state")

    # Suppliers
    cr.execute(
        """
         CREATE TABLE lunch_supplier (
            id SERIAL NOT NULL PRIMARY KEY,
            partner_id int4 NOT NULL,
            responsible_id int4,
            send_by varchar,
            automatic_email_time float8,
            recurrency_monday boolean,
            recurrency_tuesday boolean,
            recurrency_wednesday boolean,
            recurrency_thursday boolean,
            recurrency_friday boolean,
            recurrency_saturday boolean,
            recurrency_sunday boolean,
            recurrency_end_date date,
            tz varchar,
            active boolean,
            moment varchar,
            delivery varchar
         )
    """
    )

    cr.execute(
        """
        WITH vendors AS (
            SELECT supplier
              FROM lunch_order_line
             WHERE supplier IS NOT NULL
             UNION
            SELECT supplier
              FROM lunch_product
             WHERE supplier IS NOT NULL
        )
        INSERT INTO lunch_supplier(
            partner_id, tz, send_by, automatic_email_time, active, moment, delivery,
            recurrency_monday, recurrency_tuesday, recurrency_wednesday, recurrency_thursday,
            recurrency_friday, recurrency_saturday, recurrency_sunday
        )
        SELECT v.supplier, COALESCE(p.tz, 'UTC'), 'phone', 12.0, true, 'am', 'no_delivery',
               true, true, true, true, true, true, true
          FROM vendors v
          JOIN res_partner p ON p.id = v.supplier
    """
    )

    util.create_column(cr, "lunch_order_line", "supplier_id", "int4")
    util.create_column(cr, "lunch_product", "supplier_id", "int4")
    cr.execute(
        """
        UPDATE lunch_order_line l
           SET supplier_id = s.id
          FROM lunch_supplier s
         WHERE s.partner_id = l.supplier
    """
    )
    cr.execute(
        """
        UPDATE lunch_product p
           SET supplier_id = s.id
          FROM lunch_supplier s
         WHERE s.partner_id = p.supplier
    """
    )
    util.remove_field(cr, "lunch.order.line", "supplier")
    util.remove_field(cr, "lunch.product", "supplier")

    # Orders (and lines)
    util.create_column(cr, "lunch_order_line", "company_id", "int4")
    util.create_column(cr, "lunch_order_line", "currency_id", "int4")
    util.create_column(cr, "lunch_order_line", "quantity", "float8")
    util.create_column(cr, "lunch_order_line", "display_toppings", "text")
    cr.execute(
        """
        UPDATE lunch_order_line l
           SET company_id = o.company_id,
               currency_id = o.currency_id,
               quantity = 1
          FROM lunch_order o
         WHERE o.id = l.order_id
    """
    )

    util.remove_field(cr, "lunch.order.line", "order_id")
    util.remove_field(cr, "lunch.order.line", "cashmove")

    # reassign server actions, allow to keep them.
    lunch_order = model_id(cr, "lunch.order")
    lunch_order_line = model_id(cr, "lunch.order.line")
    cr.execute(
        "UPDATE ir_act_server SET model_id = %s, model_name = 'lunch.order.line' WHERE model_id = %s",
        [lunch_order_line, lunch_order]
    )
    cr.execute("UPDATE ir_act_server SET binding_model_id = %s WHERE binding_model_id = %s",
               [lunch_order_line, lunch_order])

    util.remove_model(cr, "lunch.order")
    util.rename_model(cr, "lunch.order.line", "lunch.order")

    # Product Categories
    util.create_column(cr, "lunch_product_category", "company_id", "int4")

    for n in [1, 2, 3]:
        util.create_column(cr, "lunch_product_category", "topping_label_%s" % n, "varchar")
        util.create_column(cr, "lunch_product_category", "topping_quantity_%s" % n, "varchar")

    cr.execute(
        """
        UPDATE lunch_product_category
           SET topping_label_1 = 'Supplements',
               topping_label_2 = 'Beverages',
               topping_label_3 = 'Other',
               topping_quantity_1 = '0_more',
               topping_quantity_2 = '0_more',
               topping_quantity_3 = '0_more'
    """
    )

    # Products
    util.remove_field(cr, "lunch.product", "available")

    util.create_column(cr, "res_company", "lunch_minimum_threshold", "float8")
    util.create_column(cr, "res_users", "last_lunch_location_id", "int4")

    util.remove_model(cr, "lunch.order.line.lucky")
