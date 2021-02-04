# -*- coding: utf-8 -*-

from odoo import SUPERUSER_ID

from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute(
        """
        WITH property_account AS (
            SELECT DISTINCT SUBSTRING(value_reference FROM '%,#"_*#"%' FOR '#')::int4 AS id
            FROM ir_property
            WHERE name IN (
                'property_stock_account_input',
                'property_stock_account_output',
                'property_stock_account_input_categ_id',
                'property_stock_account_output_categ_id',
                'property_account_income_id',
                'property_account_expense_id',
                'property_account_income_categ_id',
                'property_account_expense_categ_id'
            )
        )
        UPDATE account_move_line
        SET is_anglo_saxon_line = 't'
        WHERE id IN (
            SELECT aml.id
            FROM account_move_line aml
            JOIN account_move move ON move.id = aml.move_id
            JOIN account_account aa ON aa.id = aml.account_id
            JOIN property_account prop_acc ON prop_acc.id = aml.account_id
            WHERE move.type IN ('out_invoice', 'out_refund', 'out_receipt')
            AND aml.product_id IS NOT NULL
            AND aml.tax_repartition_line_id IS NULL
            AND aml.display_type IS NULL
            AND aml.exclude_from_invoice_tab
            AND aa.internal_type NOT IN ('receivable', 'payable')
        )
    """
    )

    # For other settings than (auto valuation (real_time) and FIFO costing method), stock valuation layers (SVL)
    # are created based on stock moves.
    cr.execute(
        """
        INSERT INTO stock_valuation_layer(
            create_uid,
            create_date,
            write_uid,
            write_date,
            company_id,
            product_id,
            quantity,
            unit_cost,
            value,
            remaining_qty,
            remaining_value,
            description,
            stock_move_id
        )
        SELECT
            sm.create_uid,
            sm.date,
            sm.write_uid,
            sm.date,
            sm.company_id,
            pp.id,
            CASE
                WHEN (ls.usage = 'internal' OR (ls.usage = 'transit' AND ls.company_id IS NOT NULL))
                    AND ld.usage != 'internal'
                    THEN -sm.product_qty
                WHEN ls.usage != 'internal'
                    AND (ld.usage = 'internal' OR (ld.usage = 'transit' AND ld.company_id IS NOT NULL))
                    THEN sm.product_qty
            END as quantity,
            abs(sm.price_unit),
            sm.value,
            sm.remaining_qty,
            sm.remaining_value,
            sm.reference,
            sm.id
        FROM stock_move sm
        LEFT JOIN stock_location ls ON (ls.id = sm.location_id)
        LEFT JOIN stock_location ld ON (ld.id = sm.location_dest_id)
        LEFT JOIN product_product pp ON pp.id = sm.product_id
        LEFT JOIN product_template pt ON pt.id = pp.product_tmpl_id
        LEFT JOIN product_category pc ON pc.id = pt.categ_id
        WHERE
            sm.state = 'done' AND
            'product.category,' || pc.id NOT IN
                (
                SELECT res_id FROM ir_property
                WHERE
                    name = 'property_valuation' AND
                    value_text = 'real_time' AND
                    company_id = sm.company_id
                INTERSECT
                SELECT res_id FROM ir_property
                WHERE
                    name = 'property_cost_method' AND
                    value_text = 'fifo' AND
                    company_id = sm.company_id
                )
    """
    )

    # For auto valuation (real_time) and FIFO costing method, stock valuation layers (SVL)
    # are created based on account move lines.
    cr.execute(
        """
        INSERT INTO stock_valuation_layer(
            create_uid,
            create_date,
            write_uid,
            write_date,
            company_id,
            product_id,
            quantity,
            value,
            unit_cost,
            remaining_qty,
            remaining_value,
            description,
            stock_move_id,
            account_move_id
        )
        WITH aml_value AS (
            SELECT am.stock_move_id, sum(aml.debit - aml.credit) as value, min(am.id) as move_id
              FROM account_move_line aml
              JOIN account_move am ON am.id = aml.move_id
              JOIN product_product pp ON pp.id = aml.product_id
              JOIN product_template pt ON pt.id = pp.product_tmpl_id
              WHERE am.stock_move_id IS NOT NULL
                AND 'account.account,' || aml.account_id IN
                    (SELECT value_reference FROM ir_property
                    WHERE
                        name = 'property_stock_valuation_account_id' AND
                        (res_id IS NULL OR res_id = 'product.category,' || pt.categ_id) AND
                        company_id = aml.company_id ORDER BY res_id LIMIT 1)
              GROUP BY am.stock_move_id
        )
        SELECT
            sm.create_uid,
            sm.date,
            sm.write_uid,
            sm.date,
            sm.company_id,
            sm.product_id,
            CASE
                WHEN (ls.usage = 'internal' OR (ls.usage = 'transit' AND ls.company_id IS NOT NULL))
                    AND ld.usage != 'internal'
                    THEN -sm.product_qty
                WHEN ls.usage != 'internal'
                    AND (ld.usage = 'internal' OR (ld.usage = 'transit' AND ld.company_id IS NOT NULL))
                    THEN sm.product_qty
            END as quantity,
            aml_value.value,
            abs(sm.price_unit),
            sm.remaining_qty,
            sm.remaining_value,
            sm.reference,
            sm.id,
            aml_value.move_id
        FROM stock_move sm
        LEFT JOIN stock_location ls ON (ls.id = sm.location_id)
        LEFT JOIN stock_location ld ON (ld.id = sm.location_dest_id)
        LEFT JOIN aml_value ON aml_value.stock_move_id = sm.id
        LEFT JOIN product_product pp ON pp.id = sm.product_id
        LEFT JOIN product_template pt ON pt.id = pp.product_tmpl_id
        LEFT JOIN product_category pc ON pc.id = pt.categ_id
        WHERE
            sm.state = 'done' AND
            'product.category,' || pc.id IN
                (
                SELECT res_id FROM ir_property
                WHERE
                    name = 'property_valuation' AND
                    value_text = 'real_time' AND
                    company_id = sm.company_id
                INTERSECT
                SELECT res_id FROM ir_property
                WHERE
                    name = 'property_cost_method' AND
                    value_text = 'fifo' AND
                    company_id = sm.company_id
                )
    """
    )

    # Migrate price history
    cr.execute(
        """
        WITH svl_history AS
        (
            SELECT
                svl.product_id,
                ph.datetime AS datetime,
                SUM(svl.quantity) AS quantity,
                SUM(svl.value) AS value,
                ph.cost AS new_cost,
                SUM(svl.quantity) * ph.cost - SUM(svl.value) AS corrected_value,
                svl.company_id AS company_id
            FROM product_price_history ph
            JOIN stock_valuation_layer svl ON ph.product_id = svl.product_id
            JOIN product_product pp ON pp.id = svl.product_id
            JOIN product_template pt ON pt.id = pp.product_tmpl_id
            JOIN product_category pc ON pc.id = pt.categ_id
           WHERE svl.create_date < ph.DATETIME
             AND svl.quantity != 0
             AND svl.company_id = ph.company_id
             AND ph.create_uid != %s
             AND 'product.category,' || pc.id NOT IN
                (SELECT res_id
                   FROM ir_property
                  WHERE name = 'property_cost_method'
                    AND value_text = 'fifo'
                    AND company_id = svl.company_id
                )
            GROUP BY ph.id, svl.product_id, ph.datetime, ph.cost, svl.company_id
        )
        INSERT INTO stock_valuation_layer (create_date, write_date, product_id, quantity, VALUE, description, company_id)
        SELECT
            datetime,
            datetime,
            product_id,
            0.0,
            quantity
            * new_cost
            - value
            - LAG(corrected_value, 1, 0.0) OVER (PARTITION BY product_id, company_id ORDER BY DATETIME)
            AS corrected_value,
            'Change cost to ' || new_cost,
            company_id
        FROM svl_history
        WHERE corrected_value != 0;
    """,
        (SUPERUSER_ID,),
    )

    # In some databases, the customer has played with valuation mode/costing method so the total valuation
    # of a product in stock quants may not be the same than the one in stock valuation layers.
    # For these cases, we create a new stock valuation layer per product/per company, to adjust this difference
    cr.execute(
        """
        -- get the list of products with their valuation according to existing stock quants
        WITH quant_with_sumed_values AS (
              SELECT  q.company_id,
                      q.product_id,
                      SUM(
                        ROUND(
                            CAST (
                                q.quantity
                                * COALESCE(ir.value_float, 0)
                                AS numeric
                            ),
                            cur.decimal_places
                        )
                      ) AS sum_value
                 FROM stock_quant q
            LEFT JOIN stock_location lo ON lo.id = q.location_id
                 JOIN res_company cp ON cp.id = q.company_id
                 JOIN res_currency cur ON cur.id = cp.currency_id
                 JOIN product_product pp ON pp.id = q.product_id
                 JOIN ir_property ir ON ir.name = 'standard_price'
                      AND ir.company_id = q.company_id
                      AND ir.res_id = 'product.product,' || pp.id
                WHERE lo.usage = 'internal' OR lo.usage = 'transit'
                                    AND lo.company_id IS NOT NULL
             GROUP BY q.company_id, q.product_id
        ),

        -- get the list of products with their valuation according to existing stock valuation layer
        svl_with_sumed_values AS (
              SELECT company_id, product_id, SUM(COALESCE(value, 0)) AS sum_value
                FROM stock_valuation_layer
            GROUP BY company_id, product_id
        )

        -- add a new layer for every products which have a not the same global valuation in stock moves
        -- and in stock valuation layers
        INSERT INTO stock_valuation_layer(
            company_id,
            product_id,
            quantity,
            value,
            unit_cost,
            description
        )
        SELECT svl.company_id,
               pp.id,
               0,
               COALESCE(qt.sum_value, 0) - svl.sum_value,
               0,
               'upgrade: adjust valuation inconsistency'
          FROM product_product pp
     LEFT JOIN quant_with_sumed_values qt ON qt.product_id = pp.id
          JOIN svl_with_sumed_values svl ON svl.product_id = pp.id
          JOIN product_template pt ON pt.id = pp.product_tmpl_id
          JOIN product_category pc ON pc.id = pt.categ_id
         WHERE ('product.category,' || pc.id IN (
                SELECT res_id FROM ir_property
                 WHERE name = 'property_cost_method'
                   AND value_text IN ('standard', 'average')
                   AND company_id = svl.company_id
         )
            OR (
                NOT EXISTS (
                    SELECT 1 FROM ir_property
                    WHERE name = 'property_cost_method'
                    AND company_id = svl.company_id
                    AND res_id = 'product.category,' || pc.id
                )
                AND EXISTS (
                    SELECT 1 FROM ir_property
                    WHERE name = 'Cost Method Property'
                    AND value_text IN ('standard', 'average')
                )
            )
           )
           AND (qt.company_id IS NULL OR qt.company_id = svl.company_id)
           AND (qt.product_id IS NULL OR qt.product_id = svl.product_id)
           AND COALESCE(qt.sum_value, 0) != svl.sum_value
    """
    )

    util.remove_field(cr, "stock.move", "value")
    util.remove_field(cr, "stock.move", "remaining_qty")
    util.remove_field(cr, "stock.move", "remaining_value")
