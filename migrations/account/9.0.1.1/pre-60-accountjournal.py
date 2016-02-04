# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    """
        Journal of type sale_refund and purchase_refund have disappeared
    """
    cr.execute("""UPDATE account_journal
                    SET type = CASE WHEN type='sale_refund' THEN 'sale' 
                                WHEN type='purchase_refund' THEN 'purchase'
                                END
                    WHERE type in ('sale_refund', 'purchase_refund')
                """)

    """
        We only show on dashboard journals of type sale, purchase, cash and bank
    """
    util.create_column(cr, 'account_journal', 'show_on_dashboard', 'bool')

    cr.execute("""UPDATE account_journal
        SET show_on_dashboard = 't'
        WHERE type IN ('sale', 'purchase', 'cash', 'bank')""")
