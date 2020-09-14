# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # Manage new is_anglo_saxon_line field.
    cr.execute(
        """
        UPDATE account_move_line aml
        SET is_anglo_saxon_line = 't'
        FROM account_account account
        WHERE account.id IN (
            SELECT DISTINCT SUBSTRING(value_reference FROM '%,#"_*#"%' FOR '#')::int4
            FROM ir_property
            WHERE name IN (
                'property_stock_account_input',
                'property_stock_account_output',
                'property_stock_account_input_categ_id',
                'property_stock_account_output_categ_id',
                'property_valuation',
                'property_account_creditor_price_difference',
                'property_account_creditor_price_difference_categ'
            )
        )
        AND account.id = aml.account_id
    """
    )
    cr.execute('''
        UPDATE account_move_line aml
        SET is_anglo_saxon_line = 'f'
        WHERE NOT aml.exclude_from_invoice_tab
    ''')

    # Product in manual valuation
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
            sm.create_date,
            sm.write_uid,
            sm.write_date,
            sm.company_id,
            pp.id,
            CASE
                WHEN (ls.usage = 'internal' OR ls.usage = 'transit' AND ls.company_id IS NOT NULL) AND ld.usage != 'internal' THEN -sm.product_qty
                WHEN ls.usage != 'internal' AND (ld.usage = 'internal' OR ld.usage = 'transit' AND ld.company_id IS NOT NULL) THEN sm.product_qty
            END as quantity,
            sm.price_unit,
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
            sm.value != 0 AND
            'product.category,' || pc.id NOT IN
                (SELECT res_id FROM ir_property
                WHERE
                    name = 'property_valuation' AND
                    value_text = 'real_time' AND
                    company_id = sm.company_id)
    """
    )

    # Product in automated valuation
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
        SELECT
            aml.create_uid,
            aml.create_date,
            aml.write_uid,
            aml.write_date,
            aml.company_id,
            aml.product_id,
            aml.quantity,
            aml.debit - aml.credit,
            sm.price_unit,
            sm.remaining_qty,
            sm.remaining_value,
            aml.ref,
            am.stock_move_id,
            aml.move_id
        FROM account_move_line aml
        LEFT JOIN account_move am ON am.id = aml.move_id
        INNER JOIN stock_move sm ON am.stock_move_id = sm.id
        LEFT JOIN product_product pp ON pp.id = aml.product_id
        LEFT JOIN product_template pt ON pt.id = pp.product_tmpl_id
        LEFT JOIN product_category pc ON pc.id = pt.categ_id
        WHERE
            'account.account,' || aml.account_id IN
                (SELECT value_reference FROM ir_property
                WHERE
                    name = 'property_stock_valuation_account_id' AND
                    (res_id IS NULL OR res_id = 'product.category,' || pt.categ_id) AND
                    company_id = aml.company_id ORDER by res_id LIMIT 1) AND
            'product.category,' || pc.id IN
                (SELECT res_id FROM ir_property
                WHERE
                    name = 'property_valuation' AND
                    value_text = 'real_time' AND
                    company_id = aml.company_id)
    """
    )

    util.remove_field(cr, "stock.move", "value")
    util.remove_field(cr, "stock.move", "remaining_qty")
    util.remove_field(cr, "stock.move", "remaining_value")
