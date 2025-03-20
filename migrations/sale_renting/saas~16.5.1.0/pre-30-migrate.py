from odoo.upgrade import util


def migrate(cr, version):
    util.remove_model(cr, "rental.wizard")
    util.remove_field(cr, "rental.order.wizard.line", "is_late")
    util.remove_field(cr, "rental.order.wizard", "has_late_lines")
    util.remove_field(cr, "sale.order", "has_late_lines")
    util.remove_field(cr, "sale.order.line", "is_late")

    util.create_column(cr, "sale_order", "rental_start_date", "timestamp without time zone")
    util.create_column(cr, "sale_order", "rental_return_date", "timestamp without time zone")
    columns = util.get_columns(
        cr, "sale_order", ignore=("id", "create_uid", "create_date", "write_uid", "write_date", "name")
    )

    util.create_column(cr, "sale_order", "_upg_rental_parent_so_id", "integer")
    util.create_column(cr, "sale_order", "_upg_rental_linked_sol_ids", "integer[]")

    # create new SO if different rental periods
    query = util.format_query(
        cr,
        """
        WITH rental_lines AS (
            -- generate groups per sale order of pairs of start/return date
            SELECT order_id,
                   TO_CHAR(start_date, 'yyyy/mm/dd hh24:MI') char_start_date,
                   TO_CHAR(return_date, 'yyyy/mm/dd hh24:MI') char_return_date,
                   ARRAY_AGG(id) ids,
                   ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY TO_CHAR(start_date, 'yyyy/mm/dd hh24:MI'), TO_CHAR(return_date, 'yyyy/mm/dd hh24:MI')) num
              FROM sale_order_line
             WHERE start_date IS NOT NULL
               AND return_date IS NOT NULL
               AND is_rental = true
          GROUP BY char_start_date, char_return_date, order_id
          ORDER BY order_id, char_start_date, char_return_date
        ),
        small_tab AS (
            -- we need to create new sale order for those with multiple
            -- start/return pairs of dates, here we keep extra groups
            SELECT *
              FROM rental_lines
             WHERE num > 1
        ),
        new_ids AS (
            INSERT INTO sale_order({original_columns}, create_date, name, _upg_rental_parent_so_id, _upg_rental_linked_sol_ids)
                 SELECT {so_columns}, NOW() at time zone 'UTC', CONCAT(so.name, '-', small_tab.num), small_tab.order_id, small_tab.ids
                   FROM sale_order AS so
                   JOIN small_tab
                     ON so.id = small_tab.order_id
              RETURNING id, _upg_rental_linked_sol_ids
        )
        UPDATE sale_order_line
           SET order_id = new_ids.id
          FROM new_ids
         WHERE sale_order_line.id = ANY(new_ids._upg_rental_linked_sol_ids)
        """,
        original_columns=columns,
        so_columns=columns.using(alias="so"),
    )
    cr.execute(query)

    if cr.rowcount:
        util.add_to_migration_reports(
            """The rental period is now defined on the order, and is the same for all rented
            products. Orders with several rental periods were split into several orders with a
            similar name in order this constraint to be fulfilled.
            """,
            category="Rental",
            format="text",
        )

    # update SO period from SOL
    # we now know each SO has max one period from their lines.
    util.explode_execute(
        cr,
        """
        UPDATE sale_order
           SET rental_start_date = sol.start_date,
               rental_return_date = sol.return_date
          FROM sale_order_line sol
         WHERE sale_order.id = sol.order_id
           AND sol.is_rental = true
        """,
        table="sale_order",
    )

    util.remove_constraint(cr, "sale_order_line", "sale_order_line_rental_period_coherence")
    util.remove_column(cr, "sale_order_line", "start_date")
    util.remove_column(cr, "sale_order_line", "return_date")
    util.remove_column(cr, "sale_order", "has_pickable_lines")
    util.remove_column(cr, "sale_order", "has_returnable_lines")
