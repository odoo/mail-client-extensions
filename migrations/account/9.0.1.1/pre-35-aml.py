# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

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

    util.create_column(cr, 'account_move_line', 'invoice_id', 'int4')
    cr.execute("""UPDATE account_move_line aml
                    SET invoice_id = inv.id
                    FROM account_invoice inv
                    WHERE inv.move_id = aml.move_id
                """)