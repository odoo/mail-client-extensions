# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):

    # There was an unfortunate oversight during upgrade 6.1 -> 7.0 that leave the
    # fields `number` and `subtotal`. Remove them now to avoid duplicated entries.
    util.remove_field(cr, "account.cashbox.line", "number")
    util.remove_field(cr, "account.cashbox.line", "subtotal")

    util.create_column(cr, "account_cashbox_line", "cashbox_id", "int4")
    util.rename_field(cr, "account.cashbox.line", "pieces", "coin_value")
    util.rename_field(cr, "account.cashbox.line", "number_opening", "number")
    util.rename_field(cr, "account.cashbox.line", "subtotal_opening", "subtotal")

    util.create_column(cr, "account_bank_statement", "cashbox_start_id", "int4")
    util.create_column(cr, "account_bank_statement", "cashbox_end_id", "int4")

    cr.execute("""
        CREATE TABLE account_bank_statement_cashbox (
            id SERIAL PRIMARY KEY,
            create_uid integer,
            create_date timestamp without time zone,
            write_uid integer,
            write_date timestamp without time zone
        )
    """)

    # NOTE: reuse create_uid as linked bank_statement_id
    cr.execute("""
        WITH cashbox AS (
            INSERT INTO account_bank_statement_cashbox (create_uid)
                 SELECT UNNEST(ARRAY[bank_statement_id, bank_statement_id])
                   FROM account_cashbox_line
               GROUP BY bank_statement_id
              RETURNING id, create_uid AS bs_id
        )
        UPDATE account_bank_statement s
           SET cashbox_start_id = c.start_id,
               cashbox_end_id = c.end_id
          FROM (SELECT bs_id,
                       MIN(id) AS start_id,
                       MAX(id) AS end_id
                  FROM cashbox
              GROUP BY bs_id) c
         WHERE s.id = c.bs_id
    """)
    cr.execute("UPDATE account_bank_statement_cashbox SET create_uid = NULL")

    cr.execute("""
        UPDATE account_cashbox_line l
           SET cashbox_id = s.cashbox_start_id
          FROM account_bank_statement s
         WHERE s.id = l.bank_statement_id
    """)
    cr.execute("""
        INSERT INTO account_cashbox_line(create_uid, create_date, write_uid, write_date,
                                         coin_value, number, cashbox_id)
             SELECT l.create_uid, l.create_date, l.write_uid, l.write_date,
                    l.coin_value, l.number_closing, s.cashbox_end_id
               FROM account_cashbox_line l
               JOIN account_bank_statement s ON s.id = l.bank_statement_id
    """)

    util.remove_field(cr, "account.cashbox.line", "number_closing")
    util.remove_field(cr, "account.cashbox.line", "subtotal_closing")
    util.remove_field(cr, "account.cashbox.line", "bank_statement_id")
