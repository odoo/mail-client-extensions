# -*- coding: utf-8 -*-
def migrate(cr, version):
    # m2o function fields now have foreign keys...
    cr.execute("""UPDATE pos_session
                     SET cash_register_id = NULL
                   WHERE cash_register_id NOT IN (SELECT id
                                                    FROM account_bank_statement)
                     AND state = 'closed'
               """)

    cr.execute("""UPDATE pos_session
                     SET cash_journal_id = NULL
                   WHERE cash_journal_id NOT IN (SELECT id
                                                   FROM account_journal)
                     AND state = 'closed'
               """)
