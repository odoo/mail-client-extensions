import odoo

from odoo.upgrade import util
from odoo.upgrade.util import json


def migrate(cr, version):
    # Update repair_order values according to refactored model and create/update stock_move based on repair_line
    util.create_column(cr, "repair_order", "procurement_group_id", "integer")

    util.explode_execute(
        cr,
        """
        -- Create procurement_group and bind them to their repair_order
          WITH new_proc AS (
               INSERT INTO procurement_group (
                           partner_id, name, move_type, create_uid,
                           write_uid, create_date, write_date
                         )
                    SELECT r.partner_id, r.name, 'direct', r.create_uid,
                           r.write_uid, NOW()::TIMESTAMP, NOW()::TIMESTAMP
                      FROM repair_order r
                     WHERE {parallel_filter}
                 RETURNING id, name
             )
        UPDATE repair_order r
           SET procurement_group_id = proc.id
          FROM new_proc proc
         WHERE r.name = proc.name
        """,
        alias="r",
        table="repair_order",
    )
    util.remove_constraint(cr, "repair_order", "repair_order_name")

    # 'To invoice' state no longer exists as it's now delegated to a bind Sale Order
    # We create/get and assign an adapted tag to ROs in such state so that the user can keep track of them
    cr.execute("SELECT id FROM repair_tags WHERE name = 'To Invoice'")
    tag_id = cr.fetchone()
    if not tag_id:
        cr.execute(
            """
            INSERT INTO repair_tags (
                        color, create_uid, write_uid, name,
                        create_date, write_date
                      )
                 VALUES (
                        1, %s, %s, 'To Invoice',
                        NOW()::TIMESTAMP, NOW()::TIMESTAMP
                      )
              RETURNING id
            """,
            [odoo.SUPERUSER_ID, odoo.SUPERUSER_ID],
        )
        tag_id = cr.fetchone()

    query = """
    INSERT INTO repair_order_repair_tags_rel (repair_order_id, repair_tags_id)
         SELECT r.id, %s
           FROM repair_order r
          WHERE r.state = '2binvoiced'
    """
    util.explode_execute(cr, cr.mogrify(query, tag_id).decode(), alias="r", table="repair_order")

    # repair_order values according to refactored model
    util.change_field_selection_values(cr, "repair.order", "state", {"ready": "confirmed"})
    # 2binvoiced state's update depends on invoice_method
    util.explode_execute(
        cr,
        """
            UPDATE repair_order
               SET state = CASE invoice_method
                                WHEN 'b4repair' THEN 'draft'
                                ELSE 'under_repair'
                           END
             WHERE state = '2binvoiced'
        """,
        table="repair_order",
    )
    # Update domains based on '2binvoiced' state

    def adapter(leaf, _or, _neg):
        left, op, right = leaf
        if op == "=":
            op = "in"
            right = [right]
        elif op == "!=":
            op = "not in"
            right = [right]
        if isinstance(right, (tuple, list)) and "2binvoiced" in right:
            right.remove("2binvoiced")
            right.extend(("draft", "under_repair"))
        return [(left, op, right)]

    util.domains.adapt_domains(cr, "repair.order", "state", "state", adapter=adapter)

    # sale_order_id -> name kept but usage totally changed !!!
    util.explode_execute(cr, "UPDATE repair_order SET sale_order_id = NULL", table="repair_order")

    # guarantee_limit (date yyy-mm-dd) -> under_warranty (bool)
    util.create_column(cr, "repair_order", "under_warranty", "boolean")
    util.explode_execute(
        cr,
        """
        UPDATE repair_order r
           SET under_warranty = TRUE
         WHERE r.guarantee_limit IS NOT NULL
           AND (
                   r.state = 'done'
                   OR r.guarantee_limit >= NOW()::date
               )
           AND {parallel_filter}
        """,
        alias="r",
        table="repair_order",
    )

    # invoice_id -> Field deleted, now done through a sale.order, set reference in Internal Notes
    # fees_lines -> Model and field deleted, now done through sale_order, backup infos in Internal Notes
    query = util.format_query(
        cr,
        """
        WITH repair_fee_taxes AS (
             SELECT m2m.repair_fee_line_id as fee_id,
                    string_agg(t.name->>'en_US', ',') as taxes
               FROM repair_fee_line_tax m2m
               JOIN repair_fee rf
                 ON m2m.repair_fee_line_id = rf.id
               JOIN repair_order ro
                 ON rf.repair_id = ro.id
               JOIN account_tax t
                 ON m2m.tax_id = t.id
              WHERE {{parallel_filter}}
           GROUP BY m2m.repair_fee_line_id
           ),
             repair_operation_notes AS (
             SELECT f.repair_id,
                    CONCAT(
                          '<h2>Operations</h2>
                          <table class="table table-bordered o_table">
                          <thead><tr>
                          <td><h4>Product</h4></td>
                          <td><h4>Description</h4></td>
                          <td><h4>Quantity</h4></td>
                          <td><h4>Unit Price</h4></td>
                          <td><h4>Taxes</h4></td>
                          <td><h4>Tax Excl.</h4></td>
                          <td><h4>Tax Incl.</h4></td>
                          <td><h4>Invoiced</h4></td>
                          </tr></thead>
                          <tbody>',
                          string_agg(
                                    CONCAT(
                                          '<tr>',
                                          '<td>', {}, '</td>',
                                          '<td>', {}, '</td>',
                                          '<td>', f.product_uom_qty, '</td>',
                                          '<td>', f.price_unit, '</td>',
                                          '<td>', {}, '</td>',
                                          '<td>', f.price_subtotal, '</td>',
                                          '<td>', f.price_total, '</td>',
                                          '<td>',
                                          CASE WHEN f.invoiced=TRUE
                                               THEN 'Yes'
                                               ELSE ''
                                          END,
                                          '</td>',
                                          '</tr>'
                                          ),
                                    E'\n' ORDER BY f.id
                                    ),
                          '</tbody></table>'
                          ) AS operation_notes
               FROM repair_fee f
               JOIN repair_order ro
                 ON f.repair_id = ro.id
               JOIN product_product p
                 ON f.product_id = p.id
               JOIN product_template pt
                 ON p.product_tmpl_id = pt.id
          LEFT JOIN repair_fee_taxes ft
                 ON ft.fee_id = f.id
              WHERE {{parallel_filter}}
           GROUP BY f.repair_id
           )
      UPDATE repair_order r
         SET internal_notes = CONCAT(
                                 CASE
                                    WHEN acc.id IS NOT NULL THEN
                                     CONCAT(
                                        '<h2>Invoice reference</h2>',
                                        '<p>Name: ', {}, '</p>',
                                        '<p>Id: ', acc.id, '</p><hr>'
                                     )
                                    ELSE ''
                                 END,
                                 COALESCE(op.operation_notes, ''),
                                     '<h2>Quotation notes</h2>',
                                     r.quotation_notes, '<hr>',
                                     '<h2>Internal notes</h2>',
                                     r.internal_notes
                                    )
        FROM repair_order ro
   LEFT JOIN account_move acc
          ON ro.invoice_id = acc.id
   LEFT JOIN repair_operation_notes op
          ON ro.id = op.repair_id
       WHERE r.id = ro.id
             AND {{parallel_filter}}
        """,
        util.pg_html_escape("pt.name->>'en_US'"),
        util.pg_html_escape("f.name"),
        util.pg_html_escape("ft.taxes"),
        util.pg_html_escape("acc.name"),
    )
    util.explode_execute(cr, query, alias="ro", table="repair_order")

    # For repair_line already linked to a move_id, set the repair_line_type and price_unit on the move
    util.create_column(cr, "stock_move", "repair_line_type", "varchar")
    util.explode_execute(
        cr,
        """
        UPDATE stock_move m
           SET repair_line_type = l.type,
               price_unit = l.price_unit
          FROM repair_line l
         WHERE m.id = l.move_id
        """,
        alias="m",
        table="stock_move",
    )

    # When repair_line is not already linked to a move_id, create it
    util.explode_execute(
        cr,
        """
          WITH r_line AS (
                      SELECT l.id, l.repair_id, r.company_id, l.product_id, l.product_uom,
                             l.product_uom_qty, l.location_id, l.location_dest_id, l.create_uid,
                             l.write_uid, l.create_date, l.write_date, r.name,
                             l.price_unit, l.type AS repair_line_type, l.state, r.name AS origin,
                             r.procurement_group_id AS group_id,
                             CASE
                                  WHEN r.schedule_date IS NOT NULL
                                  THEN r.schedule_date::TIMESTAMP
                                  ELSE
                                       r.create_date
                             END date
                        FROM repair_line l
                  INNER JOIN repair_order r
                          ON l.repair_id = r.id
                       WHERE l.move_id IS NULL
                         AND {parallel_filter}
                       ORDER BY l.id
             ),
               new_move AS (
                        INSERT INTO stock_move
                                    (
                                     repair_id, company_id, product_id, product_uom,
                                     product_uom_qty, location_id, location_dest_id, create_uid,
                                     write_uid, create_date, write_date, name,
                                     price_unit, repair_line_type, state, origin,
                                     group_id, date, procure_method, sequence --sequence is used as an hijacked column
                                    )
                             SELECT l.repair_id, l.company_id, l.product_id, l.product_uom,
                                    l.product_uom_qty, l.location_id, l.location_dest_id, l.create_uid,
                                    l.write_uid, l.create_date, l.write_date, l.name,
                                    l.price_unit, l.repair_line_type, l.state, l.origin,
                                    l.group_id, l.date, 'make_to_stock', l.id
                               FROM r_line l
                          RETURNING id, sequence AS line_id
             ),
               _dummy AS (
                      UPDATE repair_line line
                         SET move_id = nm.id
                        FROM new_move nm
                       WHERE line.id = nm.line_id
             )
        UPDATE stock_move m
           SET sequence = NULL
          FROM new_move
         WHERE m.id = new_move.id
        """,
        alias="l",
        table="repair_line",
    )

    # Create a move_line for repair_line that has a lot_id
    if not util.column_exists(cr, "stock_move_line", "reserved_qty"):
        util.explode_execute(
            cr,
            """
            INSERT INTO stock_move_line
                        (company_id, product_id, product_uom_id, location_id, location_dest_id,
                        state, date, move_id,
                        quantity,
                        lot_id, lot_name)
                 SELECT l.company_id, l.product_id, l.product_uom, l.location_id, l.location_dest_id,
                        m.state, m.date, l.move_id,
                        CASE
                            WHEN t.tracking = 'serial'
                            THEN 1.0
                            ELSE m.quantity
                        END quantity,
                        l.lot_id, lot.name
                   FROM repair_line l
                   JOIN stock_lot lot
                        ON l.lot_id = lot.id
                   JOIN stock_move m
                        ON l.move_id = m.id
                        AND m.state != 'done'
                   JOIN product_product p
                        ON l.product_id = p.id
                   JOIN product_template t
                        ON p.product_tmpl_id = t.id
            """,
            alias="l",
            table="repair_line",
        )
    else:
        util.explode_execute(
            cr,
            """
            INSERT INTO stock_move_line
                        (company_id, product_id, product_uom_id, location_id, location_dest_id,
                        state, reserved_qty, reserved_uom_qty, date, move_id,
                        qty_done,
                        lot_id, lot_name)
                 SELECT l.company_id, l.product_id, l.product_uom, l.location_id, l.location_dest_id,
                        m.state, 0.0 AS reserved_qty, 0.0 AS reserved_uom_qty, m.date, l.move_id,
                        CASE
                            WHEN t.tracking = 'serial'
                            THEN 1.0
                            ELSE m.quantity_done
                        END quantity_done,
                        l.lot_id, lot.name
                   FROM repair_line l
                   JOIN stock_lot lot
                        ON l.lot_id = lot.id
                   JOIN stock_move m
                        ON l.move_id = m.id
                        AND m.state != 'done'
                   JOIN product_product p
                        ON l.product_id = p.id
                   JOIN product_template t
                        ON p.product_tmpl_id = t.id
            """,
            alias="l",
            table="repair_line",
        )

    # Clean refactored models
    util.remove_field(cr, "repair.order", "tax_calculation_rounding_method")
    util.remove_field(cr, "repair.order", "description")
    util.remove_field(cr, "repair.order", "address_id")
    util.remove_field(cr, "repair.order", "default_address_id")
    util.remove_field(cr, "repair.order", "pricelist_id")
    util.remove_field(cr, "repair.order", "currency_id")
    util.remove_field(cr, "repair.order", "partner_invoice_id")
    util.remove_field(cr, "repair.order", "invoice_method")
    util.remove_field(cr, "repair.order", "invoice_id")
    util.remove_field(cr, "repair.order", "fees_lines")
    util.remove_field(cr, "repair.order", "invoiced")
    util.remove_field(cr, "repair.order", "repaired")
    util.remove_field(cr, "repair.order", "amount_untaxed")
    util.remove_field(cr, "repair.order", "amount_tax")
    util.remove_field(cr, "repair.order", "amount_total")
    util.remove_field(cr, "repair.order", "invoice_state")
    util.remove_field(cr, "repair.order", "quotation_notes")
    util.remove_field(cr, "repair.order", "guarantee_limit")
    util.remove_field(cr, "repair.order", "operations")

    util.remove_field(cr, "account.payment", "repair_ids")

    util.remove_field(cr, "account.bank.statement.line", "repair_ids")

    util.remove_field(cr, "account.move", "repair_ids")

    util.remove_field(cr, "account.move.line", "repair_fee_ids")
    util.remove_field(cr, "account.move.line", "repair_line_ids")

    util.remove_view(cr, "repair.view_make_invoice")
    util.delete_unused(cr, "repair.act_repair_invoice")
    util.delete_unused(cr, "repair.mail_template_repair_quotation")
    util.delete_unused(cr, "repair.repair_line_rule")
    util.delete_unused(cr, "repair.repair_fee_rule")

    util.remove_model(cr, "repair.line")
    util.remove_model(cr, "repair.fee")
    util.remove_model(cr, "repair.order.make_invoice")

    # Deactivate old ir_sequence with code "repair.order"
    s_id = util.ref(cr, "repair.seq_repair")
    if s_id:
        cr.execute(
            "UPDATE ir_sequence s SET active = FALSE WHERE s.id = %s",
            [s_id],
        )

    # To avoid NULL insertion in location_xxx_id during computation occuring between pre and post migration scripts
    # We must create the repair_operation picking type_id(s) and link it to existing warehouse(s)
    util.create_column(cr, "stock_warehouse", "repair_type_id", "integer")
    util.create_column(cr, "stock_picking_type", "default_remove_location_dest_id", "integer")
    util.create_column(cr, "stock_picking_type", "default_recycle_location_dest_id", "integer")

    # create picking sequence
    cr.execute(
        """
        INSERT INTO ir_sequence
                    (
                        number_next, number_increment, padding, company_id, create_uid, write_uid,
                        name, implementation, prefix, active,
                        create_date, write_date
                    )
             SELECT 1, 1, 5, wh.company_id, %s, %s,
                    wh.name || ' Sequence repair', 'standard', wh.code || '/RO/',
                    TRUE, NOW()::TIMESTAMP, NOW()::TIMESTAMP
               FROM stock_warehouse wh
              ORDER BY wh.id
          RETURNING id
        """,
        [odoo.SUPERUSER_ID, odoo.SUPERUSER_ID],
    )
    new_seq_ids = [res[0] for res in cr.fetchall()]

    util.parallel_execute(
        cr,
        [
            util.format_query(cr, "CREATE SEQUENCE {} INCREMENT BY 1 START WITH 1", f"ir_sequence_{seq_id:03}")
            for seq_id in new_seq_ids
        ],
    )

    # If enterprise/stock_barcode is installed, also set << restrict_put_in_pack = 'optional' >> into stock_picking_type
    # values are used by formating rather than by using cr.execute's parameter as we want to avoid cast of blank string
    if util.column_exists(cr, "stock_picking_type", "restrict_put_in_pack"):
        columns = util.ColumnList.from_unquoted(
            cr,
            [
                "restrict_put_in_pack",
                "restrict_scan_tracking_number",
                "restrict_scan_source_location",
                "restrict_scan_dest_location",
            ],
        ).using(leading_comma=True)
        static_values = util.SQLStr(", 'optional', 'optional', 'no', 'optional'")
    else:
        columns = static_values = util.SQLStr("")

    # Create repair picking_type for each warehouse
    query = util.format_query(
        cr,
        """
        WITH new_pt AS (
             INSERT INTO stock_picking_type
                         (name, code, default_location_src_id, default_location_dest_id,
                         default_remove_location_dest_id, default_recycle_location_dest_id, sequence_code, warehouse_id,
                         company_id, active,
                         barcode,
                         reservation_method, create_backorder, show_operations, create_uid, write_uid,
                         use_create_lots, use_existing_lots, show_reserved, is_repairable,
                         create_date, write_date
                         {})
                  SELECT DISTINCT ON(wh.id)
                         jsonb_build_object('en_US', 'Repairs'), 'repair_operation', wh.lot_stock_id, loc.id,
                         sloc.id, wh.lot_stock_id, 'RO', wh.id,
                         wh.company_id, wh.active,
                         UPPER(REPLACE(wh.code, ' ', '')) || '-RO',
                         'at_confirm', 'ask', TRUE, %(uid)s, %(uid)s,
                         TRUE, TRUE, TRUE, FALSE,
                         NOW()::TIMESTAMP, NOW()::TIMESTAMP
                         {}
                    FROM stock_warehouse wh
               LEFT JOIN stock_location loc
                      ON loc.company_id = wh.company_id
                     AND loc.usage = 'production'
               LEFT JOIN stock_location sloc
                      ON sloc.company_id = wh.company_id
                     AND sloc.scrap_location = 't'
                   ORDER BY wh.id, loc.id, sloc.id
               RETURNING id, warehouse_id
           )
           UPDATE stock_warehouse wh
              SET repair_type_id = new_pt.id
             FROM new_pt
            WHERE new_pt.warehouse_id = wh.id
        RETURNING repair_type_id
        """,
        columns,
        static_values,
    )
    cr.execute(query, {"uid": odoo.SUPERUSER_ID})
    new_pt_ids = [res[0] for res in cr.fetchall()]

    # Update sequence and seq_id on new picking_type
    cr.execute(
        """
        WITH info AS (
           SELECT MAX(pt.sequence) + 1 AS start
             FROM stock_picking_type pt
            WHERE pt.sequence IS NOT NULL
        )
        UPDATE stock_picking_type pt
           SET sequence_id = (%s::jsonb->>pt.id::text)::int,
               sequence = seq.num
          FROM info,
               generate_series(info.start, info.start + %s) AS seq(num)
         WHERE pt.id IN %s
        """,
        [json.dumps(dict(zip(new_pt_ids, new_seq_ids))), len(new_pt_ids), tuple(new_pt_ids)],
    )

    # To avoid errors, and useless imports followed by post_migration deletion,
    # manually create "picking_type_warehouse0_repair" in ir_model_data
    cr.execute(
        """
        INSERT INTO ir_model_data
                    (res_id, noupdate, name,
                    module, model,
                    create_date, write_date)
             SELECT pt.id, TRUE, 'picking_type_warehouse0_repair',
                    'repair', 'stock.picking.type',
                    NOW()::TIMESTAMP, NOW()::TIMESTAMP
               FROM ir_model_data d
               JOIN stock_picking_type pt
                 ON pt.warehouse_id = d.res_id
              WHERE d.module = 'stock'
                AND d.name = 'warehouse0'
                AND pt.code = 'repair_operation'
              ORDER BY pt.id
              LIMIT 1
        """,
    )

    # Force value on new repair computed fields
    util.create_column(cr, "repair_order", "picking_type_id", "integer")

    # As the user was before allowed to individually specify the src and dest locations for each repair_line,
    # the behavior, DS and logic of the new repair module are not fully retro-compatible with old-style repair orders
    # in case we import such an old & incompatible repair order that's still in draft,
    # we set it's state to 'confirm' in order to lock the global location edition in the repair order.
    cr.execute(
        """
            WITH line AS (
                  SELECT m.repair_id,
                         m.location_id,
                         m.location_dest_id,
                         m.repair_line_type
                    FROM stock_move m
                    JOIN repair_order r
                      ON r.id = m.repair_id
                   WHERE m.repair_line_type IS NOT NULL
                     AND r.state = 'draft'
                   GROUP BY (m.repair_id, m.location_id, m.location_dest_id, m.repair_line_type)
               ),
                 lock AS (
                  SELECT l.repair_id as id
                    FROM line l
                   GROUP BY l.repair_id
                  HAVING COUNT(l) > COUNT(DISTINCT l.repair_line_type)
               )
          UPDATE repair_order r
             SET state = 'confirmed'
            FROM lock l
           WHERE l.id = r.id
             AND r.state = 'draft'
        """
    )

    # For each repair_order, search and assign picking_type of the most repeated location of associated repair_lines
    util.explode_execute(
        cr,
        """
            WITH repair_wh AS (
                SELECT DISTINCT ON (m.repair_id)
                       m.repair_id AS r_id,
                       loc.warehouse_id AS wh_id,
                       COUNT(*) AS count
                  FROM stock_move m
                  JOIN stock_location loc
                    ON loc.id = ANY(ARRAY[m.location_id, m.location_dest_id])
                  JOIN stock_warehouse wh
                    ON loc.warehouse_id = wh.id
                 WHERE m.repair_line_type IS NOT NULL
                   AND m.repair_id IS NOT NULL
                   AND m.company_id = wh.company_id
                 GROUP BY m.repair_id, loc.warehouse_id
                 ORDER BY m.repair_id ASC, m.count DESC, loc.warehouse_id ASC
               )
          UPDATE repair_order r
             SET picking_type_id = wh.repair_type_id
            FROM repair_wh map
      INNER JOIN stock_warehouse wh
              ON wh.id = map.wh_id
           WHERE r.id = map.r_id
        """,
        alias="r",
        table="repair_order",
    )
    # For ROs without repair_line, assign picking_type from default_warehouse on basis of company_id.
    # INFO : company_id is a mandatory field on repair_order
    util.explode_execute(
        cr,
        """
            WITH default_wh AS (
                        SELECT r.id r_id,
                               MIN(wh.id) wh_id
                          FROM repair_order r
                          JOIN stock_warehouse wh
                            ON r.company_id = wh.company_id
                     LEFT JOIN stock_move m
                            ON m.repair_id = r.id
                           AND m.repair_line_type IS NOT NULL
                         WHERE m.id IS NULL
                           AND wh.active = TRUE
                           AND {parallel_filter}
                         GROUP BY r_id
               )
          UPDATE repair_order r
             SET picking_type_id = wh.repair_type_id
            FROM default_wh map
      INNER JOIN stock_warehouse wh
              ON map.wh_id = wh.id
           WHERE map.r_id = r.id
        """,
        alias="r",
        table="repair_order",
    )

    # Maybe location_id was personalized out of the new picking_type on the RO,
    # Pre computing location_dest_id, parts_location_id, recycle_location_id is not only optimal
    # but it also avoids overriding the existing location_id that's set on the same compute
    util.create_column(cr, "repair_order", "location_dest_id", "integer")
    util.create_column(cr, "repair_order", "parts_location_id", "integer")
    util.create_column(cr, "repair_order", "recycle_location_id", "integer")

    util.explode_execute(
        cr,
        """
            UPDATE repair_order r
               SET location_dest_id = pt.default_location_dest_id,
                   parts_location_id = pt.default_remove_location_dest_id,
                   recycle_location_id = pt.default_recycle_location_dest_id
              FROM stock_picking_type pt
             WHERE pt.id = r.picking_type_id
        """,
        alias="r",
        table="repair_order",
    )

    # Set 'picking_type_id' and 'warehouse_id' in stock_move
    util.explode_execute(
        cr,
        """
        UPDATE stock_move m
           SET picking_type_id = r.picking_type_id,
               warehouse_id = pt.warehouse_id
          FROM repair_order r
          JOIN stock_picking_type pt
            ON pt.id = r.picking_type_id
         WHERE m.repair_id = r.id
           AND m.repair_line_type IS NOT NULL
        """,
        alias="m",
        table="stock_move",
    )
