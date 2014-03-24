# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util
def migrate(cr, version):
    # m2o function fields now have foreign keys...

    cr.execute("""SELECT count(1)
                    FROM pos_session
                   WHERE cash_register_id NOT IN (SELECT id
                                                    FROM account_bank_statement)
               """)
    if cr.fetchone()[0]:
        util.remove_column(cr, 'pos_session', 'cash_register_id')

    cr.execute("""SELECT count(1)
                    FROM pos_session
                   WHERE cash_journal_id NOT IN (SELECT id
                                                   FROM account_journal)
               """)
    if cr.fetchone()[0]:
        util.remove_column(cr, 'pos_session', 'cash_journal_id')
