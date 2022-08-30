# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """CREATE TABLE IF NOT EXISTS sale_temporal_recurrence (
        id SERIAL PRIMARY KEY,
        create_uid integer,
        create_date timestamp without time zone,
        write_uid integer,
        write_date timestamp without time zone,
        name varchar,
        duration integer,
        unit varchar
    )"""
    )

    cr.execute("ALTER TABLE sale_temporal_recurrence ADD COLUMN _mig_rental_pricing_id integer[]")
    cr.execute(
        """
        WITH rp AS (  SELECT rp.duration,
                             rp.unit,
                             array_agg(rp.id) agg
                        FROM rental_pricing rp
                    GROUP BY rp.duration,
                             rp.unit)
        UPDATE sale_temporal_recurrence str
           SET _mig_rental_pricing_id = rp.agg
          FROM rp
         WHERE str.duration = rp.duration
           AND str.unit = rp.unit
        """
    )
    cr.execute(
        """
        WITH rp AS (   SELECT rp.duration,
                              rp.unit,
                              array_agg(rp.id) agg
                         FROM rental_pricing rp
                    LEFT JOIN sale_temporal_recurrence str
                           ON str.duration = rp.duration
                          AND str.unit = rp.unit
                        WHERE str.id IS NULL
                     GROUP BY rp.duration,
                              rp.unit)
        INSERT INTO sale_temporal_recurrence (duration, unit, _mig_rental_pricing_id)
        SELECT rp.duration, rp.unit, rp.agg
          FROM rp
        """
    )

    cr.execute(
        """
        INSERT INTO product_pricing (currency_id,recurrence_id,price,product_template_id)
             SELECT currency_id,str.id,price,product_template_id
               FROM rental_pricing rp
               JOIN sale_temporal_recurrence str ON rp.id = ANY (str._mig_rental_pricing_id)
        """
    )
    # move the rental values into temp columns and in post, update the values
    util.create_column(cr, "sale_order_line", "start_date", "timestamp without time zone")
    cr.execute(
        """
        UPDATE sale_order_line SET start_date=pickup_date
         WHERE pickup_date IS NOT NULL
        """
    )
    util.remove_model(cr, "rental.pricing")
    util.remove_field(cr, "sale.order.line", "rental_updatable")
    util.remove_view(cr, "sale_renting.product_template_rental_tree_view")
    util.remove_view(cr, "sale_renting.product_template_rental_kanban_view")
