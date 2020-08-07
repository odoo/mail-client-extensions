# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "stock_valuation_layer", "stock_landed_cost_id", "int4")

    util.remove_field(cr, "stock.move", "landed_cost_value")

    # Get every account moves linked to a landed cost, create a valuation layer for them.
    cr.execute(
        """
        INSERT INTO stock_valuation_layer(
            create_uid,
            create_date,
            write_uid,
            write_date,
            company_id,
            product_id,
            value,
            description,
            account_move_id,
            stock_landed_cost_id
        )
        SELECT
            am.create_uid,
            am.create_date,
            am.write_uid,
            am.write_date,
            am.company_id,
            aml.product_id,
            aml.debit - aml.credit,
            aml.ref,
            lc.account_move_id,
            lc.id
        FROM stock_landed_cost lc
        JOIN account_move am ON am.id = lc.account_move_id
        JOIN account_move_line aml ON aml.move_id = am.id
        JOIN product_product pp ON pp.id = aml.product_id
        JOIN product_template pt ON pt.id = pp.product_tmpl_id
        WHERE
            'account.account,' || aml.account_id IN
                (SELECT value_reference FROM ir_property
                WHERE
                    name = 'property_stock_valuation_account_id' AND
                    (res_id IS NULL OR res_id = 'product.category,' || pt.categ_id) AND
                    company_id = aml.company_id ORDER by res_id LIMIT 1) AND
            'product.category,' || pt.categ_id IN
                (SELECT res_id FROM ir_property
                WHERE
                    name = 'property_valuation' AND
                    value_text = 'real_time' AND
                    company_id = aml.company_id)
        """)
