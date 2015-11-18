# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute("""UPDATE account_move_line aml
        SET date_maturity = inv.date_due
        FROM (SELECT date_due, move_id FROM account_invoice) inv
        WHERE aml.move_id = inv.move_id AND aml.date_maturity IS NULL
        """)

    cr.execute("""UPDATE account_move_line aml
        SET date_maturity = date
        WHERE aml.date_maturity IS NULL
        """)
