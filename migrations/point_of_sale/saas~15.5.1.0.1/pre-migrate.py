# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "pos.config", "barcode_nomenclature_id")
    util.remove_field(cr, "res.config.settings", "pos_barcode_nomenclature_id")
    util.remove_field(cr, "pos.config", "module_pos_loyalty")
    util.remove_field(cr, "res.config.settings", "pos_module_pos_loyalty")

    util.create_column(cr, "pos_session", "cash_register_balance_end_real", "numeric", default=0)
    util.create_column(cr, "pos_session", "cash_register_balance_start", "numeric", default=0)

    util.parallel_execute(
        cr,
        util.explode_query_range(
            cr,
            """
            UPDATE pos_session
               SET cash_register_balance_end_real = account_bank_statement.balance_end_real,
                   cash_register_balance_start = account_bank_statement.balance_start
              FROM account_bank_statement
             WHERE pos_session.cash_register_id = account_bank_statement.id
            """,
            table="account_bank_statement",
        ),
    )

    util.create_column(cr, "account_bank_statement_line", "pos_session_id", "int4")
    util.parallel_execute(
        cr,
        util.explode_query_range(
            cr,
            """
            UPDATE account_bank_statement_line
               SET pos_session_id = account_bank_statement.pos_session_id
              FROM account_bank_statement
             WHERE account_bank_statement_line.statement_id = account_bank_statement.id
               AND account_bank_statement.pos_session_id IS NOT NULL
            """,
            table="account_bank_statement",
        ),
    )

    util.remove_model(cr, "pos.open.statement")

    util.remove_field(cr, "account.bank.statement", "pos_session_id")
    util.remove_field(cr, "account.bank.statement", "account_id")

    util.remove_field(cr, "pos.session", "cash_register_id")
    util.remove_field(cr, "pos.session", "cash_real_difference")
    util.remove_field(cr, "pos.session", "cash_real_expected")
    util.remove_field(cr, "pos.session", "statement_ids")

    util.remove_view(cr, "point_of_sale.view_bank_statement_pos_session")
    util.remove_view(cr, "point_of_sale.account_cashbox_line_view_tree")
