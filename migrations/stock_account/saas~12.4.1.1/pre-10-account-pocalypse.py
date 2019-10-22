# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "account_move_line", "is_anglo_saxon_line", "boolean")

    # Manage new is_anglo_saxon_line field.
    cr.execute('''
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
                'property_stock_account_output_categ_id'
            )
        )
        AND account.id = aml.account_id
    ''')
